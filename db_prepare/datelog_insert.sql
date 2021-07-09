create trigger datelog_insert after insert on datelog for each row begin 
update fly set flew=true where fdate<new.today and flew=false;

update fly set off_real=(select (off_due + interval round((50+50*rand())*(1-punctual)) minute) from flight where flight.id=fid) 
where off_real is NULL and flew=true;

update fly set land_real =
timediff(off_real, ( select timediff(off_due,land_due) from flight where flight.id=fid and land_due<off_due))
where flew=true and off_real is not NULL and land_real is NULL;

end