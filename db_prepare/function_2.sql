create function seat_ticket(ticket_id int) 
returns char(30) 
begin 
declare type_p int; 
declare ffid_p int; 
declare num_p int; 
set type_p=(select stype from porder where id=(select oid from ticket where id=ticket_id));
set ffid_p=(select ffid from porder where id=(select oid from ticket where id=ticket_id));
set num_p=(select count(*) from porder inner join ticket on ticket.oid=porder.id where ffid=ffid_p and stype=type_p and ticket.id<=ticket_id  and porder.valid=2);
if type_p=1 then return concat('F', cast(num_p as char));
elseif type_p=2 then return concat('C', cast(num_p as char));
else return concat('Y', cast(num_p as char));
end if;
end

