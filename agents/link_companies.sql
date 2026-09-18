-- Domain -> company, for bizDave.
--
-- An email domain is the most reliable account key David has: 485 distinct domains
-- across his contacts, 794 across his leads, and almost no free webmail in either.
-- This builds the companies table from those domains, links every contact to its
-- company, and fills in a lead's company where only the address was known.
--
-- Idempotent and additive. It creates no company that already exists, and it only
-- ever fills a blank — it never overwrites a name David typed himself.
--
--   psql "$BIZDAVE_DB_URL" -f agents/link_companies.sql
--
-- Costs no Lovable credits and no model tokens. It is a database job, not an AI one.

begin;

-- Free webmail tells you nothing about an employer, so those addresses are skipped
-- rather than turned into a company called "gmail.com".
create temp table _dom on commit drop as
with free(d) as (values
  ('gmail.com'),('yahoo.com'),('hotmail.com'),('outlook.com'),('icloud.com'),('aol.com'),
  ('me.com'),('msn.com'),('live.com'),('protonmail.com'),('proton.me'),('googlemail.com'),
  ('comcast.net'),('verizon.net'),('sbcglobal.net'),('walla.com'),('walla.co.il'),
  ('mail.com'),('gmx.com'),('yandex.com'),('qq.com'),('163.com'),('163.net'),('inbox.com'),
  ('zoho.com'),('fastmail.com'),('hush.com'),('ymail.com'),('rocketmail.com'),('att.net'),
  ('bellsouth.net'),('cox.net'),('earthlink.net'),('juno.com'),('mac.com'),('mailinator.com')),
src as (
  select user_id, lower(split_part(email,'@',2)) dom, nullif(btrim(company),'') co
    from contacts where email like '%@%'
  union all
  select user_id, lower(split_part(email,'@',2)), nullif(btrim(company),'')
    from leads where email like '%@%'
)
select user_id, dom, co from src
where dom <> '' and dom like '%.%' and dom not in (select d from free);

-- One canonical name per domain: the one the most records already agree on, with the
-- shortest spelling winning a tie ("Front Row Group" over "Front Row Group, LLC.").
create temp table _name on commit drop as
select user_id, dom, co from (
  select user_id, dom, co,
         row_number() over (partition by user_id, dom order by count(*) desc, length(co), co) rn
  from _dom where co is not null group by user_id, dom, co
) r where rn = 1;

-- A domain nobody has ever named becomes a company named after the domain itself.
-- That is honest and obviously machine-made, which is the point — it reads as
-- something to tidy, not as a fact David asserted.
insert into companies (user_id, name, domain, website, notes, created_at, updated_at)
select d.user_id, coalesce(n.co, d.dom), d.dom, 'https://'||d.dom,
       case when n.co is null
            then '[BDAgent] No company name on record — named from the email domain.'
            else '[BDAgent] Matched from email domain.' end,
       now(), now()
from (select distinct user_id, dom from _dom) d
left join _name n on n.user_id = d.user_id and n.dom = d.dom
where not exists (select 1 from companies c where c.user_id = d.user_id and lower(c.domain) = d.dom);

-- Link contacts to their company. Only fills a blank link.
update contacts c set company_id = co.id, updated_at = now()
from companies co
where co.user_id = c.user_id
  and lower(co.domain) = lower(split_part(c.email,'@',2))
  and c.email like '%@%' and c.company_id is null;

-- Fill a lead's company where the address was all we had.
update leads l set company = co.name, updated_at = now()
from companies co
where co.user_id = l.user_id
  and lower(co.domain) = lower(split_part(l.email,'@',2))
  and l.email like '%@%' and (l.company is null or btrim(l.company) = '');

-- And a contact whose company name was blank but whose domain we now know.
update contacts c set company = co.name, updated_at = now()
from companies co
where co.id = c.company_id and (c.company is null or btrim(c.company) = '');

commit;
