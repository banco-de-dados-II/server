use bd2;

delimiter $

drop procedure if exists bd2.card_da_pessoa;

create procedure bd2.card_da_pessoa (IN q_pessoa_id INT)
begin
    select *
    from card
    where card.id in (
           select tarefa_id
           from tarefas_has_pessoas
           where tarefas_has_pessoas.pessoa_id = q_pessoa_id
    );
end $

delimiter ;
