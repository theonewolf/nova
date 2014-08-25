CREATE TABLE `introspected_entities` (
      `created_at` datetime DEFAULT NULL,
      `updated_at` datetime DEFAULT NULL,
      `deleted_at` datetime DEFAULT NULL,
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `instance_uuid` varchar(36) DEFAULT NULL,
      `drive_id` varchar(255) DEFAULT NULL,
      `introspection_target` varchar(255) DEFAULT NULL,
      `deleted` int(11) DEFAULT NULL,
      PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
