CREATE TABLE "User"
(
    id       int,
    name     VARCHAR(255) NOT NULL,
    surname  VARCHAR(255) NOT NULL,
    login    VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

ALTER TABLE "User"
    ADD PRIMARY KEY (id);


ALTER TABLE "User"
    ADD CONSTRAINT unique_login UNIQUE (login);

CREATE SEQUENCE user_id_sequence START 1;


-------- student incr

CREATE OR REPLACE FUNCTION incr_User() RETURNS trigger AS
$$
BEGIN
    NEW.id = nextval('user_id_sequence');
    return NEW;
END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER User_increment
    BEFORE insert
    ON "User"
    FOR EACH ROW
EXECUTE PROCEDURE incr_User();

---------------------------------------------------------------------------------------------------------

CREATE TABLE "Admin"
(
    id       int,
    login    VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

ALTER TABLE "Admin"
    ADD PRIMARY KEY (id);

CREATE SEQUENCE admin_id_sequence START 1;

-------- admin incr

CREATE OR REPLACE FUNCTION incr_admin() RETURNS trigger AS
$$
BEGIN
    NEW.id = nextval('admin_id_sequence');
    return NEW;
END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER admin_increment
    BEFORE insert
    ON "Admin"
    FOR EACH ROW
EXECUTE PROCEDURE incr_admin();


---------------------------------------------------------------------------------------------------------

CREATE TABLE "Exercise"
(
    id          int,
    title       VARCHAR(255) NOT NULL,
    muscle_type VARCHAR(255) NOT NULL,
    description VARCHAR(255)
);

ALTER TABLE "Exercise"
    ADD PRIMARY KEY (id);

ALTER TABLE "Exercise"
    ADD CONSTRAINT unique_Exercise_combination UNIQUE (title);

CREATE SEQUENCE Exercise_id_sequence START 1;

-------- professor incr

CREATE OR REPLACE FUNCTION incr_Exercise() RETURNS trigger AS
$$
BEGIN
    NEW.id = nextval('Exercise_id_sequence');
    return NEW;
END;

$$ LANGUAGE plpgsql;


CREATE TRIGGER Exercise_increment
    BEFORE insert
    ON "Exercise"
    FOR EACH ROW
EXECUTE PROCEDURE incr_Exercise();


---------------------------------------------------------------------------------------------------------

CREATE TABLE "Plan"
(
    id          int,
    title       VARCHAR(255) NOT NULL,
    user_created bool not null);

ALTER TABLE "Plan"
    ADD PRIMARY KEY (id);
CREATE SEQUENCE Plan_id_sequence START 1;

-------- Plan incr

CREATE OR REPLACE FUNCTION incr_Plan() RETURNS trigger AS
$$
BEGIN
    NEW.id = nextval('Plan_id_sequence');
    return NEW;
END;

$$ LANGUAGE plpgsql;


CREATE TRIGGER Plan_increment
    BEFORE insert
    ON "Plan"
    FOR EACH ROW
EXECUTE PROCEDURE incr_Plan();

---------------------------------------------------------------------------------------------------------



CREATE TABLE "Plan_exercises"
(
    id          int,
    plan_fk     int NOT NULL,
    exercise_id int NOT NULL,
    weight      int not null,
    count       int not null
);

ALTER TABLE "Plan_exercises"
    ADD PRIMARY KEY (id);
ALTER TABLE "Plan_exercises"
    ADD CONSTRAINT FOREIGN_KEY_Plan_exercises FOREIGN KEY (plan_fk) REFERENCES "Plan" (id);
CREATE SEQUENCE Plan_exercises_id_sequence START 1;


-------- Plan_exercises incr

CREATE OR REPLACE FUNCTION incr_Plan_exercises() RETURNS trigger AS
$$
BEGIN
    NEW.id = nextval('Plan_exercises_id_sequence');
    return NEW;
END;

$$ LANGUAGE plpgsql;


CREATE TRIGGER Plan_exercises_increment
    BEFORE insert
    ON "Plan_exercises"
    FOR EACH ROW
EXECUTE PROCEDURE incr_Plan_exercises();

---------------------------------------------------------------------------------------------------------


CREATE TABLE "Training"
(
    id      int,
    user_id int,
    plan_id int,
    date    Date
);

CREATE SEQUENCE Training_id_sequence START 1;

ALTER TABLE "Training"
    ADD PRIMARY KEY (id);

ALTER TABLE "Training"
    ADD CONSTRAINT FOREIGN_KEY_Training_Student FOREIGN KEY (user_id) REFERENCES "User" (id);

-------- discipline incr

CREATE OR REPLACE FUNCTION incr_Training() RETURNS trigger AS
$$
BEGIN
    NEW.id = nextval('Training_id_sequence');
    return NEW;
END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER Training_increment
    BEFORE insert
    ON "Training"
    FOR EACH ROW
EXECUTE PROCEDURE incr_Training();

---------------------------------------------------------------------------------------------------------




