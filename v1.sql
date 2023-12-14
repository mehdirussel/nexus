// Use DBML to define your database structure
// Docs: https://dbml.dbdiagram.io/docs


Table users {
  id integer [primary key]
  username varchar
  email varchar
  created_at timestamp
  password varchar
  is_super integer
  pdp varchar
}

Table messages {
  id integer [primary key]
  canal_id integer
  texte text 
  sender_id integer
  status varchar
  sent_at timestamp
}

Table canal {
  id integer [primary key]
  nom text 
  photo varchar
  superuser_id integer
}

Table est_dans_canal{
  id_user integer
  id_canal integer
}

Table invitations {
  canal_id integer
  lien varchar
  created_at timestamp
}

Table est_moderateur{
  id_user integer
  id_canal integer
}

Ref: users.id < est_dans_canal.id_user
Ref: canal.id < est_dans_canal.id_canal

Ref: users.id < est_moderateur.id_user
Ref: canal.id < est_moderateur.id_canal

Ref: messages.sender_id < users.id

Ref: messages.canal_id < canal.id

Ref: invitations.canal_id < canal.id
