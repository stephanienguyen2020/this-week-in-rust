from urllib.parse import urlsplit

url = "https://www.meetup.com/mv-rust-meetup/events/299803577/"
split_url = urlsplit(url)
clean_path = "/".join((split_url.path).split("/")[:2])
organizerUrl = split_url.scheme + "://" + split_url.netloc + clean_path + "/"
organizerName = (split_url.path).split("/")[1]

print(split_url)
print(clean_path)
print(organizerUrl)
print(organizerName)