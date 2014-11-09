USE `accounts`;

CREATE TABLE `user` (
    `id` int(10) unsigned NOT NULL auto_increment,
    `name` varchar(32) NOT NULL,
    `pass` varbinary(64) NOT NULL,
    `family_id` int(10) unsigned NOT NULL,
    `last_login` TIMESTAMP NOT NULL,
    `settle_day` int(10) unsigned NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

CREATE TABLE `account` (
    `id` int(10) unsigned NOT NULL auto_increment,
    `user_id` int(10) unsigned NOT NULL,
    `title` varchar(32) NOT NULL,
    `delete_flag` tinyint(3) unsigned NOT NULL default '0',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

CREATE TABLE `type` (
    `id` int(10) unsigned NOT NULL auto_increment,
    `title` varchar(32) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

CREATE TABLE `bill` (
    `id` int(10) unsigned NOT NULL auto_increment,
    `account_from_id` int(10) unsigned NOT NULL,
    `account_to_id` int(10) unsigned NOT NULL,
    `date` DATE NOT NULL,
    `type_id` int(10) unsigned NOT NULL,
    `amount` decimal(9,2) unsigned NOT NULL,
    `claim_flag` tinyint(3) unsigned NOT NULL default '0',
    `description` varchar(32) default NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1;

CREATE TABLE `summary` (
    `user_id` int(10) unsigned NOT NULL,
    `date` DATE NOT NULL,
    `type_id` int(10) unsigned NOT NULL,
    `income` decimal(9,2) unsigned NOT NULL,
    `outgo` decimal(9,2) unsigned NOT NULL,
    `budget` decimal(9,2) unsigned NOT NULL,
    `balance` decimal(9,2) unsigned NOT NULL,
    PRIMARY KEY (`user_id`, `date`, `type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
