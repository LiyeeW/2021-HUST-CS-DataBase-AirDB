create role company_ad;
create view cad_flight as select * from flight where
    concat((select name from company where company.id=flight.cid), '@localhost' ) = user();
create view cad_fly as select * from fly where
    concat((select name from company where company.id=
    (select cid from flight where flight.id=fly.fid)), '@localhost' ) = user();
create view cad_ticket as select pid, stype, valid, oid, seat, passwd
    from ticket inner join porder on porder.id=ticket.oid where
    concat((select name from company where company.id=
    (select cid from flight where flight.id=(select fid from fly where fly.id=(
    select ffid from porder where porder.id=oid)))), '@localhost' ) = user();
grant all privileges on airdb.cad_flight to company_ad;
grant all privileges on airdb.cad_fly to company_ad;
grant all privileges on airdb.cad_ticket to company_ad;

update mysql.user set Grant_priv='Y',Super_priv='Y' ;
flush privileges;