import instaloader
import pandas as pd
from datetime import datetime

L = instaloader.Instaloader()

username = 'thevarunmayya'

try:
    profile = instaloader.Profile.from_username(L.context, username)
except instaloader.exceptions.ProfileNotExistsException:
    print(f"Profile '{username}' does not exist.")
    exit()
except instaloader.exceptions.PrivateProfileNotFollowedException:
    print(f"Profile '{username}' is private and cannot be accessed.")
    exit()

post_data = []

for post in profile.get_posts():

    if post.typename == 'GraphSidecar':
        post_type = 'carousel'
    elif post.typename == 'GraphVideo':
        post_type = 'reels'
    else:
        post_type = 'static'

    post_info = {
        'post_id': post.mediaid,
        'post_type': post_type,
        'likes': post.likes,
        'comments': post.comments,
        'timestamp': post.date_utc.strftime('%Y-%m-%d %H:%M:%S'),
        'caption': post.caption,
        'url': f"https://www.instagram.com/p/{post.shortcode}/",
    }
    post_data.append(post_info)

    if len(post_data) >= 50:
        break

df = pd.DataFrame(post_data)

output_file = f'{username}_instagram_posts.csv'
df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")