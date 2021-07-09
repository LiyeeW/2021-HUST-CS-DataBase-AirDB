create trigger flight_insert after insert on flight for each row begin 
declare d int; 
declare bdatetime datetime; 
set bdatetime = CONCAT(new.begin,' ', TIME(NOW()));
set d = TO_DAYS(new.end)-TO_DAYS(new.begin); 
while d >= 0 do insert into fly value (0,new.id,DATE(bdatetime),false,null,null,new.av_pf,new.av_pc,new.av_py); 
set bdatetime = bdatetime + interval 1 day;
set d = d-1;
end while;
end
