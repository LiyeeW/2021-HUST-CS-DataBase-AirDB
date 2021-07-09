create trigger generate_ticket after update on fly for each row begin 
declare i int;
declare c int;
declare n int;
if new.flew = true and old.flew=false then
set n=(select count_ticket(new.id,3));
set c=(select numy from aircraft where aircraft.id=(select acid from flight where flight.id=new.fid));
set i=round(0.3*c*(1+rand()));
while (n+i)>c do set i = round(i/2+1); end while;
set n=n+i;
insert into porder value (0, new.id, 3, null, (select today from datelog order by today desc limit 1), time(now()), 2, i);
set n=(select max(id) from porder where porder.valid=2);
set c=(select max(id) from ticket);
while i>0 do
set c=c+1;
insert into ticket value (c,null,n,null,null,null);
update ticket set seat=(select seat_ticket(c)) where id=c;
set i=i-1;
end while;
end if;
end
