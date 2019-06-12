1. 清理占用的端口
```shell
yixiaoyang@[/devel/git/osc/flasker/flask-crm] % ps aux|grep erl
rabbitmq 31236 12.0  0.9 5349772 78112 ?       Ssl  16:20   0:02 /usr/lib/erlang/erts-10.4.1/bin/beam.smp -W w -A 128 -MBas ageffcbf -MHas ageffcbf -MBlmbcs 512 -MHlmbcs 512 -MMmcs 30 -P 1048576 -t 5000000 -stbt db -zdbbl 128000 -K true -- -root /usr/lib/erlang -progname erl -- -home /var/lib/rabbitmq -- -pa /usr/lib/rabbitmq/lib/rabbitmq_server-3.7.15/ebin  -noshell -noinput -s rabbit boot -sname rabbit@localhost -boot start_sasl -kernel inet_default_connect_options [{nodelay,true}] -rabbit tcp_listeners [{"0.0.0.0",5672}] -sasl errlog_type error -sasl sasl_error_logger false -rabbit lager_log_root "/var/log/rabbitmq" -rabbit lager_default_file "/var/log/rabbitmq/rabbit@localhost.log" -rabbit lager_upgrade_file "/var/log/rabbitmq/rabbit@localhost_upgrade.log" -rabbit enabled_plugins_file "/etc/rabbitmq/enabled_plugins" -rabbit plugins_dir "/usr/lib/rabbitmq/plugins:/usr/lib/rabbitmq/lib/rabbitmq_server-3.7.15/plugins" -rabbit plugins_expand_dir "/var/lib/rabbitmq/mnesia/rabbit@localhost-plugins-expand" -os_mon start_cpu_sup false -os_mon start_disksup false -os_mon start_memsup false -mnesia dir "/var/lib/rabbitmq/mnesia/rabbit@localhost" -kernel inet_dist_listen_min 25672 -kernel inet_dist_listen_max 25672
rabbitmq 31332  0.0  0.0   3652    92 ?        S    16:20   0:00 /usr/lib/erlang/erts-10.4.1/bin/epmd -daemon
rabbitmq 31579  0.0  0.0   2300   692 ?        Ss   16:20   0:00 erl_child_setup 1024
yixiaoy+ 31813  0.0  0.0   9220  2356 pts/0    S+   16:20   0:00 grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn erl
yixiaoyang@[/devel/git/osc/flasker/flask-crm] % sudo kill 31332 31236
yixiaoyang@[/devel/git/osc/flasker/flask-crm] % sudo rabbitmq-server -detached
Warning: PID file not written; -detached was passed.
```

2. 新rabbitMQ建用户名和组
```
yixiaoyang@[/devel/git/osc/flasker/flask-crm] % sudo rabbitmqctl add_user admin 123456
[sudo] yixiaoyang 的密码：
Adding user "admin" ...
yixiaoyang@[/devel/git/osc/flasker/flask-crm] % sudo rabbitmqctl set_user_tags admin administrator
Setting tags for user "admin" to [administrator] ...
yixiaoyang@[/devel/git/osc/flasker/flask-crm] % sudo rabbitmqctl  set_permissions  -p  '/'  admin '.' '.' '.'
Setting permissions for user "admin" in vhost "/" ...
yixiaoyang@[/devel/git/osc/flasker/flask-crm] % sudo systemctl restart rabbitmq.service
```
