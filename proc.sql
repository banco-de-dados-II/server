use bd2;

drop procedure if exists bd2.card_da_pessoa;
drop procedure if exists bd2.equipes_da_pessoa;
drop procedure if exists bd2.projetos_da_pessoa;
drop procedure if exists bd2.equipe_adicionar_pessoa;

delimiter $

create procedure bd2.card_da_pessoa (IN q_pessoa_id INT)
begin
    select *
    from card
    where card.criador_id = q_pessoa_id
    ;
end $

create procedure bd2.equipes_da_pessoa (IN q_pessoa_id INT)
begin
    select
        distinct(equipes.id),
        projetos.titulo as projeto,
        equipes.nome as nome,
        equipes_has_pessoas.tag as tag
    from equipes
    inner join equipes_has_pessoas
    on equipes_has_pessoas.pessoa_id = q_pessoa_id
    left join projetos_has_equipes
    on projetos_has_equipes.equipe_id = equipes.id
    left join projetos
    on projetos_has_equipes.projeto_id = projetos.id
    where
        pessoa_id = q_pessoa_id and
        equipes.id = equipes_has_pessoas.equipe_id
    ;
end $

create procedure bd2.projetos_da_pessoa (IN q_pessoa_id INT)
begin
    select titulo, criacao, fazendo, conclusao, limite
    from projetos
    inner join datas
    on datas.id = projetos.data_id
    where projetos.id in (
          select projeto_id from projetos_has_pessoas
          where projetos_has_pessoas.pessoa_id = q_pessoa_id
        )
    ;
end $

create procedure bd2.equipe_adicionar_pessoa (IN q_equipe_id INT, IN q_pessoa_id INT, IN q_tag VARCHAR(50))
begin
    replace into equipes_has_pessoas (equipe_id, pessoa_id, tag)
    value (q_equipe_id, q_pessoa_id, q_tag) ;
end $

delimiter ;
