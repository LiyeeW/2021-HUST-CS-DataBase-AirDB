create procedure create_order(in fid_in int, in fdate_in date, in ftype_in int,
in uid_in int, inout n_in int)
begin
    declare sold int;
    declare total int;
    set sold=(select count(porder.num) from flight, fly, porder where flight.id=fly.fid and porder.ffid=fly.id
        and porder.stype=ftype_in and porder.valid<>0
        and porder.valid<>3 and porder.uid=uid_in and flight.id=fid_in and fly.fdate=fdate_in for update);
    if ftype_in=1 then set total=(select numf from aircraft inner join flight on aircraft.id=flight.acid where flight.id=fid_in);
    elseif ftype_in=2 then set total=(select numc from aircraft inner join flight on aircraft.id=flight.acid where flight.id=fid_in);
    else set total=(select numy from aircraft inner join flight on aircraft.id=flight.acid where flight.id=fid_in);
    end if;
    if sold+n_in<=total then
        insert into porder value (0, (select fly.id from fly inner join flight on fly.fid=flight.id
        where flight.id=fid_in and fly.fdate=fdate_in), ftype_in, uid_in, (select today from datelog
        order by today desc limit 1), time(now()), 1, n_in);
        set n_in=0;
    end if;
end


