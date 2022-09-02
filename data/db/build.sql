CREATE TABLE IF NOT EXISTS Servers(
    server_id int NOT NULL UNIQUE,
    server_name text,
    codeword text DEFAULT 'orange',
    waiting_room int,
    waiting_log int,
    warning_log int,
    member_role int,
    active_role int,
    mod_role int,
    admin_role int,
    suspended_role int,
    mod_log_msg int,
    admin_log int
);

CREATE TABLE IF NOT EXISTS Users(
    user_id int NOT NULL UNIQUE,
    is_flagged bit DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_in_server(
    server_id int NOT NULL,
    user_id int NOT NULL,
    is_in_server bit DEFAULT 1,
    FOREIGN KEY (server_id) REFERENCES Servers(server_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    UNIQUE(server_id, user_id)
);

CREATE TABLE IF NOT EXISTS Channels(
    server_id int NOT NULL,
    channel_id int NOT NULL UNIQUE,
    is_art bit DEFAULT 0,
    is_softban bit DEFAULT 0,
    is_hardban bit DEFAULT 0,
    FOREIGN KEY (server_id) REFERENCES Servers(server_id)
);

CREATE TABLE IF NOT EXISTS Profiles(
    server_id int NOT NULL,
    user_id int NOT NULL,
    description text DEFAULT '*Type `>desc [insert description]` to add a description!*',
    color text, -- DEFAULT gray

    FOREIGN KEY (server_id) REFERENCES Servers(server_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    UNIQUE(server_id, user_id)
);

CREATE TABLE IF NOT EXISTS Warns(
    server_id int NOT NULL,
    user_id int NOT NULL,
    warn_id INTEGER PRIMARY KEY AUTOINCREMENT, --incr
    description text DEFAULT 'None',
    issuer_name text,
    issuer_id int,
    warn_date text,
    message_id int,

    FOREIGN KEY (server_id) REFERENCES Servers(server_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Mods(
    server_id int NOT NULL,
    user_id int NOT NULL,
    name text,
    is_on_duty BIT DEFAULT 0,
    timezone int DEFAULT 0,

    FOREIGN KEY (server_id) REFERENCES Servers(server_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);