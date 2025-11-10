use bd2;

delimiter $

drop procedure if exists tarefas_da_pessoa;

create procedure tarefas_da_pessoa (IN pessoa_id INT)
begin
    select status, titulo
    from tarefas
    where tarefas.id in (
           select tarefa_id
           from tarefas_has_pessoas
           where tarefas_has_pessoas.pessoa_id = pessoa_id
    );
end $

delimiter ;
