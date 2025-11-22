use bd2;

drop procedure if exists bd2.card_da_pessoa;
drop procedure if exists bd2.equipes_da_pessoa;
drop procedure if exists bd2.projetos_da_pessoa;
drop procedure if exists bd2.equipe_adicionar_pessoa;
drop procedure if exists bd2.update_card;
drop procedure if exists bd2.create_card;
drop procedure if exists bd2.update_projeto;
drop procedure if exists bd2.criar_projeto;

delimiter $

create procedure bd2.card_da_pessoa (IN q_pessoa_id INT, IN q_pagina INT, IN q_max INT)
begin
    select *
    from card
    where card.atribuido_id = q_pessoa_id
    limit q_pagina, q_max;
end $

create procedure bd2.equipes_da_pessoa (IN q_pessoa_id INT, IN q_pagina INT, IN q_max INT)
begin
    select
        distinct(equipes.id),
        equipes.nome as nome,
        equipes_has_pessoas.tag as tag
    from equipes
    inner join equipes_has_pessoas on equipes_has_pessoas.equipe_id = equipes.id
    inner join projetos_has_equipes on projetos_has_equipes.equipe_id = equipes.id
    where equipes_has_pessoas.pessoa_id = q_pessoa_id
    limit q_pagina, q_max;
end $

create procedure bd2.projetos_da_pessoa (IN q_pessoa_id INT, IN q_pagina INT, IN q_max INT)
begin
    select projetos.id as id, titulo, criacao, fazendo, conclusao, limite
    from projetos
    left join datas
    on datas.id = projetos.data_id
    where projetos.id in (
          select projeto_id from projetos_has_pessoas
          where projetos_has_pessoas.pessoa_id = q_pessoa_id
        )
    limit q_pagina, q_max ;
end $

create procedure bd2.equipe_adicionar_pessoa (IN q_equipe_id INT, IN q_pessoa_id INT, IN q_tag VARCHAR(50))
begin
    replace into equipes_has_pessoas (equipe_id, pessoa_id, tag)
    value (q_equipe_id, q_pessoa_id, q_tag) ;
end $

create procedure bd2.update_card (
       IN q_id int,
       IN q_titulo varchar(100),
       IN q_tag varchar(100),
       IN q_fazendo date,
       IN q_conclusao date,
       IN q_limite date,
       IN q_status varchar(100))
begin
    update tarefas
    set titulo = q_titulo, status = q_status
    where id = q_id ;

    update datas
    set fazendo = q_fazendo, conclusao = q_conclusao, limite = q_limite
    where
    id in (select data_id from tarefas where tarefas.id = q_id) ;

    update tarefas_has_pessoas
    set tag = q_tag
    where tarefas_has_pessoas.tarefa_id = q_id ;
end $

create procedure bd2.create_card (
       IN q_titulo varchar(100),
       IN q_tag varchar(100),
       IN q_criacao date,
       IN q_fazendo date,
       IN q_conclusao date,
       IN q_limite date,
       IN q_status varchar(100),
       IN q_criador_id int)
begin
    insert into datas (criacao, fazendo, conclusao, limite)
    value (q_criacao, q_fazendo, q_conclusao, q_limite) ;

    set @data_id = LAST_INSERT_ID();

    insert into tarefas (status, titulo, projeto_id, data_id, criador_id)
    value (q_status, q_titulo, 69, @data_id, q_criador_id) ;

    SET @tarefa_id = LAST_INSERT_ID();

    insert into tarefas_has_pessoas (tarefa_id, pessoa_id, tag)
    value (@tarefa_id, q_criador_id, q_tag) ;
end $

create procedure bd2.update_projeto (
       IN q_id INT,
       IN q_titulo varchar(100),
       IN q_criacao date,
       IN q_fazendo date,
       IN q_conclusao date,
       IN q_limite date)
begin
    update datas
    set fazendo = q_fazendo, conclusao = q_conclusao, limite = q_limite
    where
    id in (select data_id from projetos where projetos.id = q_id) ;

    update projetos
    set titulo = q_titulo
    where id = q_id ;
end $

create procedure bd2.criar_projeto (
       OUT q_id INT,
       IN q_titulo varchar(100),
       IN q_criacao date,
       IN q_pessoa_id INT)
begin
    insert into datas (criacao)
    value (q_criacao);

    set @data_id = LAST_INSERT_ID();

    insert into projetos (titulo, data_id)
    value (q_titulo, @data_id);

    set q_id = LAST_INSERT_ID();

    insert into projetos_has_pessoas (projeto_id, pessoa_id, tag)
    value (q_id, q_pessoa_id, 'criador');
end $

delimiter ;

-- quais sao as 10 pessoas com mais tarefas
-- select count(pessoa_id), pessoa_id pessoa_id from tarefas_has_pessoas group by pessoa_id order by count(pessoa_id) desc limit 10;
