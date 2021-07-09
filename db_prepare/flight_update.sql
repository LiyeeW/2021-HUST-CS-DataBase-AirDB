create trigger flight_update after update on flight for each row begin 
declare d int; 
declare bdatetime datetime; 
if new.end > old.end then
set bdatetime = CONCAT(old.end,' ', TIME(NOW()));
set d = TO_DAYS(new.end)-TO_DAYS(old.end); 
while d > 0 do
set bdatetime = bdatetime + interval 1 day;
insert into fly value (0,new.id,DATE(bdatetime),false,null,null,new.av_pf,new.av_pc,new.av_py); 
set d = d-1;
end while;
end if;
end
