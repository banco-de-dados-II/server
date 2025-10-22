# tabelas

## eventos
- _id
- horario (date)
- ação (enum)
- pessoa-id (number)

## pessoas
- _id
- nome (string)
- telefone (string)
- email (string)

## tags
- _id
- categoria (string | enum)
- links (\[tags._id...\])

## tarefa log / registro / diario
- _id
- data (data)
- registro (string)