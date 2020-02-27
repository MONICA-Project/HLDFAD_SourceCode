rabbitmq-plugins enable rabbitmq_management
rabbitmqctl add_user monica monica123
rabbitmqctl set_user_tags monica administrator
rabbitmqctl set_permissions -p / monica /".*/" /".*/" /".*/"
