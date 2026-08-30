Some node-local exporters expose metrics only over Unix sockets. Targets relabeled with `__unix_socket__` are currently down or can return another target’s series when several sockets share an advertised address.

Make HTTP and HTTPS scraping through that label work correctly across configuration reloads.

Do not look for or use online solutions.
