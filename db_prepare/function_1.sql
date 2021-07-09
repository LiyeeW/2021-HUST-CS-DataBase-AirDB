create function count_ticket(ffid_p int, stype_p int) 
returns int 
return (select count(*) from porder inner join ticket on ticket.oid=porder.id where ffid=ffid_p and stype=stype_p and porder.valid=2); 
