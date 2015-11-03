#!/usr/bin/env python

import getopt, sys, os, re, socket, time, urllib2, shutil

__version__ = "hostsmerge 0.1.0"
__confpath__ = "hostsmerge.conf"

def read_config(path):
	opts = {}
	if os.path.isfile(path):
		with open(path, "r") as config_file:
			opts = parse_config(config_file.read())
	return opts

def default_paths(opts):
	if not "hostspath" in opts:
		hosts_path = ""
		if os.name == "posix":
			hosts_path = "/etc/hosts"
		elif os.name == "nt":
			hosts_path = os.path.join(os.environ["SYSTEMROOT"], "system32/drivers/etc/hosts")
		else:
			raise Exception("No hosts file found (unsupported os: " + os.name + "), specify path manually with --hostspath")
		if not os.path.isfile(hosts_path):
			raise Exception("No hosts file found in \"" + hosts_path + "\", specify path manually with --hostspath")
		opts["hostspath"] = hosts_path
	if not "backup" in opts:
		opts["backup"] = "backup"
	return opts

def parse_config(lines):
	opts = {}
	for line in lines.splitlines():
		line = re.sub(r"#.*", "", line)
		if len(line.strip()):
			groups = re.match(r"(?!-)([^\s=]+)(?:\s*=\s*(.*))?", line).groups()
			opts[groups[0]] = groups[1] if groups[1] else ""
	return opts

def parse_list(lines):
	items = []
	for line in lines.splitlines():
		items.append(line)
	return items

def read_list(path):
	print("Reading list file " + os.path.abspath(path) + "...")
	with open(path, "r") as list_file:
		lines = list_file.read()
	return parse_list(lines)

def get_list(url):
	print("Retrieving list file " + url + "...")
	return parse_list(urllib2.urlopen(urllib2.Request(url, headers={"User-Agent": "Python/urllib2"})).read())

def parse_hosts(lines):
	hosts = {}
	for line in lines.splitlines():
		line = re.sub(r"#.*", "", line)
		if len(line.strip()):
			match = re.match(r"\s*(\S*)\s*(.*)", line)
			ip = match.group(1)
			hostnames = match.group(2).split()
			if ip in hosts:
				hosts[ip].extend(hostnames)
			else:
				hosts[ip] = hostnames
	return hosts

def read_hosts(path):
	print("Reading " + os.path.abspath(path) + "...")
	with open(path, "r") as hosts_file:
		lines = hosts_file.read()
	return parse_hosts(lines)

def write_hosts(path, hosts):
	print("Writing " + os.path.abspath(path) + "...")
	outp = "# Generated by " + __version__ + " on " + time.strftime("%c") + "\n"
	for ip, hostnames in hosts.iteritems():
		for hostname in hostnames:
			outp += ip + "\t" + hostname + "\n"
	with open(path, "w") as hosts_file:
		hosts_file.write(outp.strip())

def get_hosts(url):
	print("Retrieving " + url + "...")
	return parse_hosts(urllib2.urlopen(urllib2.Request(url, headers={"User-Agent": "Python/urllib2"})).read())

def backup_rules(opts):
	if not "no-backup" in opts and (not "output" in opts or opts["hostspath"] == opts["output"]):
		if not os.path.exists(opts["backup"]):
			os.makedirs(opts["backup"])
		shutil.copy2(opts["hostspath"], os.path.join("backup", os.path.splitext(opts["hostspath"])[0] + "_" + time.strftime("%Y%m%d_%H%M%S")))

def merge_rules(opts):
	hosts = read_hosts(opts["hostspath"]) if not "new" in opts else {}
	opt_sort = "sort" in opts
	if "hostslist" in opts:
		for hostslist in opts["hostslist"].split(","):
			if os.path.isfile(hostslist):
				opts["sources"].extend(read_list(hostslist))
			else:
				opts["sources"].extend(get_list(fix_url(hostslist)))
	for uri in opts["sources"]:
		if os.path.isfile(uri):
			new_hosts = read_hosts(uri)
		else:
			new_hosts = get_hosts(fix_url(uri))
		for ip, hostnames in new_hosts.iteritems():
			if ip in hosts:
				for hostname in hostnames:
					if not hostname in hosts[ip]:
						hosts[ip].append(hostname)
			else:
				hosts[ip] = hostnames
			if opt_sort:
				hosts[ip] = sorted(hosts[ip])
	backup_rules(opts)
	write_hosts(opts["output"] if "output" in opts else opts["hostspath"], hosts)
	print("Successfully merged rules")

def get_rules(opts):
	hosts = read_hosts(opts["hostspath"])
	for query in opts["queries"]:
		query_is_ip = is_ip(query)
		found = 0
		if query_is_ip:
			if query in hosts:
				print(" ".join(hosts[query]) + " resolve(s) to " + query)
				found += 1
		else:
			for ip, hostnames in hosts.iteritems():
				if query in hostnames:
					print(query + " resolves to " + ip)
					found += 1
		if not found:
			print(query + " - nothing found")
		elif found > 1 and not query_is_ip:
			print("Warning: " + query + " resolves to multiple hostnames?")

def set_rules(opts):
	hosts = read_hosts(opts["hostspath"])
	queries = zip(opts["queries"][0::2], opts["queries"][1::2])
	opt_new = "new" in opts
	if len(opts["queries"]) % 2 != 0:
		queries.append((opts["queries"][-1], ""))
	for names, value in queries:
		value_is_ip = is_ip(value)
		names = names.split(",")
		for name in names:
			name_is_ip = is_ip(name)
			if not name_is_ip and value == "":
				for ip, hostnames in hosts.iteritems():
					if name in hostnames:
						hosts[ip].remove(name)
			elif name_is_ip and value == "":
				del hosts[name];
			elif not name_is_ip and value_is_ip:
				for ip, hostnames in hosts.iteritems():
					if name in hostnames:
						hosts[ip].remove(name)
				if not opt_new and value in hosts:
					hosts[value].append(name)
				else:
					hosts[value] = [name]
			elif name_is_ip and not value_is_ip:
				for ip, hostnames in hosts.iteritems():
					if value in hostnames:
						hosts[ip].remove(value)
				if not opt_new and name in hosts:
					hosts[name].append(value)
				else:
					hosts[name] = [value]
			elif not name_is_ip and not value_is_ip and not name == value:
				found = 0
				for ip, hostnames in hosts.iteritems():
					if name in hostnames:
						hosts[ip].remove(name)
					if value in hostnames:
						hosts[ip].append(name)
						if opt_new:
							hosts[ip].remove(value)
						found += 1
				if found <= 0:
					print(value + " - nothing found")
			elif name_is_ip and value_is_ip and not name == value:
				if value in hosts:
					if not opt_new and name in hosts:
						hosts[name] += hosts[value]
					else:
						hosts[name] = hosts[value]
					del hosts[value]
				else:
					print(value + " - nothing found")
	backup_rules(opts)
	write_hosts(opts["output"] if "output" in opts else opts["hostspath"], hosts)

def is_ip(value):
	if not ":" in value: # ipv6
		try:
			socket.inet_aton(value) # ipv4
		except socket.error:
			return False
	return True

def fix_url(url):
	if not re.match(r"^[a-zA-Z0-9]+:\/\/", url):
		url = "http://" + url
	return url

def usage():
	print("Usage:\t" + os.path.basename(sys.argv[0]) + " [options] <url|file>")

def main():
	shorthand = {"h": "help", "v": "version", "s": "set", "g": "get", "b": "no-backup", "n": "new", "o": "sort", "H": "hostspath", "B": "backup", "O": "output", "l": "hostslist"}
	try:
		copts, args = getopt.getopt(sys.argv[1:], "hvsgbnoH:B:O:l:", ["help", "version", "hostspath=", "set", "get", "no-backup", "backup=", "new", "sort", "output=", "hostslist="])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		sys.exit(2)

	try:
		opts = read_config(__confpath__)
		for o, a in copts:
			o = o.lstrip("-")
			if o in shorthand:
				o = shorthand[o]
			if o == "help":
				usage()
				return
			elif o == "version":
				print(__version__)
				return
			else:
				opts[o] = a
		opts = default_paths(opts)

		if "get" in opts:
			opts["queries"] = args
			get_rules(opts)
		elif "set" in opts:
			opts["queries"] = args
			set_rules(opts)
		else:
			opts["sources"] = args
			merge_rules(opts)
	except Exception as err:
		print("Failed: " + str(err))
		sys.exit(1)

if __name__ == "__main__":
	main()
