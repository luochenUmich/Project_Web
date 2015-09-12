drop table if exists projects;
create table projects (
	id integer primary key autoincrement,
	name text not null,
	title text not null,
	description text not null
);

drop table if exists people;
create table people (
	id integer primary key autoincrement,
	name text not null,
	project_id integer not null,
	FOREIGN KEY(project_id) REFERENCES projects(id)
);

drop table if exists news;
create table news (
	id integer primary key autoincrement,
	title text not null,
	description text not null,
	project_id integer not null,
	FOREIGN KEY(project_id) REFERENCES projects(id)
);

drop table if exists publications;
create table publications (
	id integer primary key autoincrement,
	description text not null,
	project_id integer not null,
	FOREIGN KEY(project_id) REFERENCES projects(id)
);