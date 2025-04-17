# This file is designed for developer to test the API

## Define Major Route Categories

The routes are divided into logical modules for better organization:

- **Authentication (auth)**: login, registration, logout, token management.
- **Users (users)**: profile, information modification, follow/unfollow.
- **Posts (posts)**: create, edit, delete posts, retrieve posts.
- **Comments (comments)**: add, delete comments on a post.
- **Likes (likes)**: manage likes (add, remove).
- **Messages (messages)**: send, receive private messages.
- **Notifications (notifications)**: manage alerts for likes, comments, messages, etc.

## Auth API

### Register

`POST : http://127.0.0.1:5000/auth/register`

```json
{
    "username" : "test",
    "email" : "test@gmail.com",
    "password" : "password"
}
```

It returns code **201** :

```json
{
    "message": "account created successfully."
}
```

### Login

`POST : http://127.0.0.1:5000/auth/login`

```json
{
    "username" : "test",
    "password" : "password"
}
```

It returns code **200** :

```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjRkYzcwNDEzLTEwOTQtNGY4Zi04Y2ZhLTg3YzhlYzkzMDNlYSIsImV4cCI6MTc0MDE2NjA4OX0.zc2DpJ8J07vy6WPZNeOkmc26dnLfZQQwSbuodxwss5s"
}
```

## User API

### Profile

`POST : http://127.0.0.1:5000/user/profile`

In header, you need to add `Authorization` (OAuth 2.0) with the HS256 algo get from login.`

It returns code **200** :

```json
{
    "bio": null,
    "created_at": "Fri, 21 Feb 2025 18:16:21 GMT",
    "email": "test@gmail.com",
    "profile_picture": "default.jpg",
    "username": "test",
    "website": null,
    "gender": null
}
```

### Update Profile

`POST : http://127.0.0.1:5000/user/edit`

```json
{
    "username" : "test2",
    "bio" : "I am a developer"
}
```

It returns code **200** :

```json
{
    "message": "Profile updated successfully",
    "user": {
        "bio": "I am a developer",
        "email": "test@gmail.com",
        "id": "28ff42af-b87c-4e4c-8051-3365547674d2",
        "username": "test2",
        "website": null,
        "gender": null
    }
}
```

### Upload Profile Picture

`POST : http://127.0.0.1:5000/user/upload-profile-picture`

With `Content-Type` as `multipart/form-data`
And `Authorization` (OAuth 2.0) with the HS256 algo get from login.

```json
{
    "file" : "amazing_picture.jpg"
}
```

It will download on server and returns code **200** :

```json
{
    "file_url": "/user/profile-picture/amazing_picture.jpg",
    "message": "File uploaded successfully"
}
```

### Get profile picture from path

`GET http://127.0.0.1:5000/user/profile-picture/<filename>`

`<filename>` is the name of the picture you want to get.

It returns code **200** and the media of the filename.:

![example picture](/server/public/uploads/default.jpg)

*Example of a picture when you search /default.jpg*

### Display foreign profile

`GET : http://127.0.0..1:5000/user/profile/<username>`

Switch `<username>` with the id of the user you want to get the profile.
In header, you need to add `Authorization` (OAuth 2.0) with the HS256 algo get from login. And `Content-Type` as `multipart/form-data`

It returns code **200** :

```json
{
    "bio": "Salut je suis un autre utilisateur de valenstagram",
    "message": "The user profile info",
    "profile_picture": "colin-watts-4mdlRYKQiDc-unsplash.jpg",
    "username": "test2",
    "website": ""
}
```

### Search for a user

`GET : http://127.0.0.1:5000/user/search/<username>`

Switch `<username>` with the id of the user you want to get the profile.

It returns code **200** :

```json
{
    "message": "Users found",
    "users": [
        {
            "profile_picture": "cesar-couto-VlThqxlFaE0-unsplash.jpg",
            "username": "test"
        },
        {
            "profile_picture": "colin-watts-4mdlRYKQiDc-unsplash.jpg",
            "username": "test2"
        },
        {
            "profile_picture": "default.jpg",
            "username": "test3"
        }
    ]
}
```

### Follow a user

`GET / POST :  http://127.0.0.1:5000/follow/user`

In header, you need to add `Authorization` (OAuth 2.0) with the HS256 algo get from login.

```json
{
   "username_other" : "test2"
}
```

It returns code **200** :

```json
{
    "follow": {
        "created_at": "Sun, 09 Mar 2025 01:17:17 GMT",
        "follow_id": "28ff42af-b87c-4e4c-8051-3365547674d2",
        "followed_id": "5c46a94e-c991-46ab-b14b-3f98fb220879",
        "id": "136f869b-344c-4c11-a1b1-149b15dae898"
    },
    "message": "Followed successfully"
}
```

### Unfollow a user

`GET / POST :  http://127.0.0.1:5000/follow/unfollow`

In header, you need to add `Authorization` (OAuth 2.0) with the HS256 algo get from login.

```json
{
   "username_other" : "test2"
}
```

It returns code **200** :

```json
{
    "message": "Unfollow successfully",
    "users": {
        "ex-followed-id": "5c46a94e-c991-46ab-b14b-3f98fb220879",
        "ex-follower-id": "28ff42af-b87c-4e4c-8051-3365547674d2"
    }
}
```

### Delete a follower

`GET / POST : http://127.0.0.1:5000/follow/remove-follower/`

In header, you need to add `Authorization` (OAuth 2.0) with the HS256 algo get from login.

```json
{
   "username_other" : "test"
}
```

It returns code **200** :

```json
{
    "message": "Delete follow relation successfully",
    "users": {
        "ex-followed-id": "5c46a94e-c991-46ab-b14b-3f98fb220879",
        "ex-follower-id": "28ff42af-b87c-4e4c-8051-3365547674d2"
    }
}
```

### Get followers of an user

`GET / POST : http://127.0.0.1:5000/follow/get-follow/<username>`

Switch `<username>` with the id of the user you want to get the followers.

It returns code **200** :

```json
{
    "count": 1,
    "followers": [
        {
            "followed_at": "2025-03-12T22:04:20.106989",
            "id": "28ff42af-b87c-4e4c-8051-3365547674d2",
            "profile_picture": "cesar-couto-VlThqxlFaE0-unsplash.jpg",
            "username": "test"
        }
    ]
}
```

### Get followed of an user

`GET / POST : http://127.0.0.1:5000/follow/get-followed/<username>`

Switch `<username>` with the id of the user you want to get the followers.

It returns code **200** :

```json
{
    "count": 1,
    "followed": [
        {
            "followed_at": "2025-03-12T22:04:20.106989",
            "id": "5c46a94e-c991-46ab-b14b-3f98fb220879",
            "profile_picture": "colin-watts-4mdlRYKQiDc-unsplash.jpg",
            "username": "test2"
        }
    ]
}
```

### Upload a post

`POST : http://127.0.0.1:5000/post/upload

In header, you need to add `Authorization` (OAuth 2.0) with the HS256 algo get from login. And `Content-Type` as `multipart/form-data`

```json
{
    "caption" : "This is a caption",
    "file" : "file.jpg"
}
```

Here same process as the uploading profile picture but with a different route it return code **200** :

```json
{
    "message": "Post uploaded successfully",
    "post": {
        "caption": "Look this cool picture !",
        "created_at": "2025-03-17 15:15:51.394491",
        "user_id": "28ff42af-b87c-4e4c-8051-3365547674d2"
    },
    "post_url": "/post/c7013664-db3d-45c5-a3c5-2680448170c6"
}
```

### Get a post

`GET : http://127.0.0.1:5000/post/<post_id>`

Switch `<post_id>` with the id of the post you want to get.

It returns code **200** :

```json
{
    "message": "Post found",
    "post": {
        "caption": "orem Ipsum is simply dummy text ",
        "created_at": "2025-04-13 20:52:21.537384",
        "id": "383cf999-2d11-4549-8653-ee2bbbba8faf",
        "image_url": "pic4.jpg",
        "user_profile_url": "pic3.png",
        "username": "dev"
    }
}
```

- Future implementation, you will be able to get all the comments and likes of the post.

### Display the feed for an user

`GET : http://127.0.0.1:5000/post/feed`

In header, you need to add `Authorization` (OAuth 2.0) with the HS256 algo get from login.

It returns code **200** :

```json
{
    "content": [
        {
            "caption": "Yeah this is a good picture",
            "created_at": "2025-03-27 12:13:08.325125",
            "id": "ad0e6c89-933b-4fc8-9326-8037048caa0a",
            "image_url": "Capture_decran_du_2025-03-26_10-36-02.png",
            "user_id": "9ef9ab78-5c8a-43cd-92c4-19fbd230b2a3",
            "user_profile": "cat_selfie.jpg",
            "username": "test"
        },
        {
            "caption": "OH this is a good screenshot",
            "created_at": "2025-03-27 12:12:53.098360",
            "id": "108cacf5-11f3-4410-a01f-2f740018c246",
            "image_url": "Capture_decran_du_2025-03-21_12-21-49.png",
            "user_id": "9ef9ab78-5c8a-43cd-92c4-19fbd230b2a3",
            "user_profile": "cat_selfie.jpg",
            "username": "test"
        },
        {
            "caption": "Look my cool picture ! ",
            "created_at": "2025-03-27 12:12:18.591720",
            "id": "3bab412f-a282-43d1-9b3b-f9c05fa19a11",
            "image_url": "Capture_decran_du_2025-01-16_10-48-32.png",
            "user_id": "9ef9ab78-5c8a-43cd-92c4-19fbd230b2a3",
            "user_profile": "cat_selfie.jpg",
            "username": "test"
        }
    ],
    "message": "Feed successfully loaded"
}
```
### Get all post from a user

`POST : http://127.0.0.1:5000/post/get-user/<username>`

In header you can put the Bearer token to proof yourself you are trying to see all your post (include the hidden one), but the token is not necessary for the request.

Its return code **200** :

Request with token in header (there is one post with the hidden tag - private visibility)

```json
{
    "message": "Post(s) found",
    "post": [
        {
            "caption": "orem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type an",
            "created_at": "2025-04-13 20:52:21.537384",
            "id": "383cf999-2d11-4549-8653-ee2bbbba8faf",
            "image_url": "pic4.jpg",
            "user_id": "0143e35c-3f81-4474-8f20-e92048539c42",
            "user_profile": "pic3.png",
            "username": "dev"
        },
        {
            "caption": "orem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type an",
            "created_at": "2025-04-13 20:52:15",
            "id": "b558f226-77d4-4c96-abf3-81e5d337d717",
            "image_url": "pic7.jpg",
            "user_id": "0143e35c-3f81-4474-8f20-e92048539c42",
            "user_profile": "pic3.png",
            "username": "dev"
        }
    ]
} 
```

Request without the token (public visibility)

```json
{
    "message": "Post(s) found",
    "post": [
        {
            "caption": "orem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type an",
            "created_at": "2025-04-13 20:52:21.537384",
            "id": "383cf999-2d11-4549-8653-ee2bbbba8faf",
            "image_url": "pic4.jpg",
            "user_id": "0143e35c-3f81-4474-8f20-e92048539c42",
            "user_profile": "pic3.png",
            "username": "dev"
        }
    ]
}
```