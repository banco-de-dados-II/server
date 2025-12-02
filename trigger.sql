use bd2;

drop trigger if exists bd2.novo_usuario;

delimiter $

create trigger novo_usuario after insert on pessoas
for each row begin
    insert into datas (criacao) value (current_date());

    set @data_id = LAST_INSERT_ID();
    insert into projetos (titulo, data_id) value ("minhas tarefas", @data_id);

    set @projeto_id = LAST_INSERT_ID();

    insert into projetos_has_pessoas (projeto_id, pessoa_id, direto) value (@projeto_id, new.id, true);
end $

delimiter ;
