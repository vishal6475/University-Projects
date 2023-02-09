
// A helper function to upload new images to the server
import { fileToDataUrl } from './helpers.js';

// Other helper functions defined by me
import { hideAllLikePopups } from './helpers.js';
import { showErrorAlert } from './helpers.js';
import { showCautionAlert } from './helpers.js';
import { showSuccessAlert } from './helpers.js';
import { fetchMethodHeaderWithToken } from './helpers.js';
import { clearAllRegisterFields } from './helpers.js';
import { clearAllLoginFields } from './helpers.js';
import { removeDetailsOfEditProfile } from './helpers.js';
import { convertUnixToDate } from './helpers.js';
import { addEventShowLikes } from './helpers.js';
import { addEventShowComments } from './helpers.js';
import { loadNewUserMessage } from './helpers.js';
import { updateProfileDetailsUser } from './helpers.js';


// declaring few global variables to store some details so that we don't need to call fetch several times
let token = 0;                      // to store authorization token obtained after sign-in
let loginUserId = 0;                // to store login user id
let loginUsername = '';             // to store username of login user
let userFollowingPeople = [];       // to keep track of all the users followed by logged in user
let globalOtherUserId = 0;          // to get user id of other people and push to array userFollowingPeople 
let lastPostId = 0;                 // to store the id of last post created in db
let checkUserId = 1;                // to be used in function call to get last post id
let currentPage;                    // to check on which page we are
let scrollHeight = 0;               // to store scroll height when moving from user feed to other pages
let feedLength = 5;                 // required to fetch 5 posts at a time
let feedPostsStart = 0;             // starting position to get the user feed posts
let userHasAnyFeed = 0;             // to check whether user has got any post/feed in their user feed or not


// declaring variables to store set intervals
let intervalCheckBottom;
let intervalLiveUpdateUserFeed;
let intervalLiveUpdateComments;
let intervalLiveUpdateLikes;
let intervalPostNotify;


// In the 1st part of this file, I have defined functions to all buttons like edit, update, post image etc.
// In the 2nd part, I have defined function to load post, likes and comments on all pages.
// In the 3rd part, I have defined functions to check what user is doing, where he is and which pages to shows.


// Basic function to hide all pages and their elements, runs this at the beginning to hide all items
// and later display those that are required.
const showNothing = () => {
    // scroll to top of window
    window.scrollTo(0,0); 

    currentPage = 'Other';
    document.getElementById('login-window').style.display = 'none';
    document.getElementById('registration-window').style.display = 'none'; 
    
    document.getElementById('home-feed-btn').style.display = 'none';  
    document.getElementById('home-feed-btn').style.backgroundColor = '#f7f9fa'; 
    document.getElementById('home-feed-btn').style.color = '#000000';  
    
    document.getElementById('user-profile-btn').style.display = 'none';  
    document.getElementById('user-profile-btn').style.backgroundColor = '#f7f9fa';  
    document.getElementById('user-profile-btn').style.color = '#000000'; 
    
    document.getElementById('search-user').style.display = 'none';  
    document.getElementById('logout-btn').style.display = 'none';  
    document.getElementById('user-feed-box').style.display = 'none';    
    document.getElementById('user-profile-page').style.display = 'none';
    document.getElementById('other-profile-page').style.display = 'none';
}

// initially don't show any page, based on situation, we will show page later
if (document.cookie !== 'false') {
    showNothing();
}


// 1ST PART STARTS FROM HERE
// In the 1st part of this file, I have defined functions to all buttons like edit, update, post image etc.


// to hide error alert on clicking close
document.getElementById('error-popup-close-btn').addEventListener('click', () => {
    document.getElementById('error-popup-box').style.display = 'none';
})


// to hide caution alert on clicking close
document.getElementById('caution-popup-close-btn').addEventListener('click', () => {
    document.getElementById('caution-popup-box').style.display = 'none';
    document.getElementById('caution-popup-heading').innerText = 'Caution alert:';
    document.getElementById('caution-popup-message').style.color = '#d1691d';   // orange type color 
})


// to hide success alert on clicking close
document.getElementById('success-popup-close-btn').addEventListener('click', () => {
    document.getElementById('success-popup-box').style.display = 'none';
})


// to login a user
document.getElementById("sign-in-btn").addEventListener('click', () => {

    // checking if password and confirm password match
    if (document.getElementById('username').value.length === 0) {
        showCautionAlert('Username field is empty.\nPlease fill all the fields.');
    } else if (document.getElementById('password').value !== document.getElementById('confirm-password').value) {
        showCautionAlert('Password and Confirm Passwords do not match.\nPlease try again.');
    } else {
        const loginBody = {
            "username": document.getElementById('username').value,
            "password": document.getElementById('password').value,
        };
        const loginFetch = fetch('http://localhost:5000/auth/login', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
                },
            body: JSON.stringify(loginBody),
        })
        loginFetch.then((data) => {
            if (data.status === 403) {
                showErrorAlert('Incorrect login details entered.\nPlease enter the correct details again.')
            } if (data.status === 400) {
                showCautionAlert('Missing/username password.\nPlease enter all the required details.')
            } else if (data.status === 200) {
                data.json().then(result => {
                    token = result.token;
                    document.cookie = token;

                    clearAllLoginFields();
                    
                    let enteredURL = location.hash;
                    if (enteredURL.length > 0) {
                        loadUserProfilePage();
                        loadUserFeed();
                        if (enteredURL === '#profile=me') {
                            showUserProfilePage();
                        } else if (enteredURL === '#feed') {
                            showUserFeed();    
                        } else if (enteredURL !== '#profile=me' && enteredURL.substr(0,9) === '#profile=') {
                            loadProfile(enteredURL.substring(9));            
                        }
                    } else {
                        loadPagesOnRefresh(); // to load the initial pages (like user feed, user profile) on sign-in or page refresh
                        showUserFeed(); // to show the user home page
                    }
                })
            }
        })
        .catch((error) => {
            showErrorAlert(error);
        });
    }
})


// to change screen from login to registration page
document.getElementById("register-btn").addEventListener('click', () => {
    showRegistrationWindow();
    clearAllLoginFields();
})


// to change screen from registration to login page
document.getElementById("back-btn").addEventListener('click', () => {
    showLoginWindow();
    clearAllRegisterFields();
})


// to register a user
document.getElementById("submit-btn").addEventListener('click', () => {

    // checking if any of the fields are empty
    if (document.getElementById('username-register').value === '' ||
        document.getElementById('password-register').value === ''||
        document.getElementById('confirm-register').value === ''||
        document.getElementById('email-register').value === ''||
        document.getElementById('name-register').value === '') {
            showCautionAlert('Missing required fields.\nPlease fill all the required details before clicking submit.');
    } // checking if password and confirm password match
    else if (document.getElementById('password-register').value !== document.getElementById('confirm-register').value) {
        showCautionAlert('Password and Confirm Passwords do not match.\nPlease enter the same passwords in both fields.');
    } else {
        const registerUser = {
            "username": document.getElementById('username-register').value,
            "password": document.getElementById('password-register').value,
            "email": document.getElementById('email-register').value,
            "name": document.getElementById('name-register').value,
        };
        const result = fetch('http://localhost:5000/auth/signup', {
            method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(registerUser),
        }).then((data) => {
            if (data.status === 400) {
                showCautionAlert('Missing/username password.\nPlease enter all the required details.')
            } else if (data.status === 409) {
                showErrorAlert('This username has already been taken.\nPlease try with other unique username.')
            } else if (data.status === 200) {
                data.json().then(result => {
                    token = result.token;                    
                    loadUserFeed();
                    showUserFeed();
                    clearAllRegisterFields();
                })
            }
        })
        .catch((error) => {
            showErrorAlert(error);
        });

    }
})


// to show user feed page on clicking 'home-feed-button' button
document.getElementById("home-feed-btn").addEventListener('click', () => {
    showUserFeed();
})


// to show user profile page on clicking 'user-profile-button' button
document.getElementById("user-profile-btn").addEventListener('click', () => {
    showUserProfilePage();
})


// to perform logout function
document.getElementById("logout-btn").addEventListener('click', () => {

    // clear the intervals so they don't make fetch calls when user is logged out
    clearAllIntervals();      
    clearInterval(intervalPostNotify);  
    
    // show the login window now
    showLoginWindow();
    document.cookie = 'false';

    // remove all post elements from user feed, user profile page and other users pages
    let userFeedBox = document.getElementById('user-feed-box');
    while (userFeedBox.firstChild) {
        userFeedBox.removeChild(userFeedBox.lastChild);
    }

    let userProfileFeedBox = document.getElementById('user-profile-feed-box');
    while (userProfileFeedBox.firstChild) {
        userProfileFeedBox.removeChild(userProfileFeedBox.lastChild);
    }

    let userOtherUserFeedBox = document.getElementById('other-profile-feed-box');
    while (userOtherUserFeedBox.firstChild) {
        userOtherUserFeedBox.removeChild(userOtherUserFeedBox.lastChild);
    }

    // removing the locally stored values for the logged-in user    
    token = 0;
    loginUserId = 0;
    loginUsername = '';
    userFollowingPeople = []
})


// adding event listener to allow logged in user to search for any user and see their profile page
document.getElementById('search-user').addEventListener('keyup', (event) => {
    if (event.key === 'Enter' && event.target.value.length > 0) {   
        
        let userName = event.target.value;
        const fetchUser = fetch(`http://localhost:5000/user/?username=${userName}`, fetchMethodHeaderWithToken('GET', token))
        .then((fetchUserObj) => {
            if (fetchUserObj.status === 200) {
                loadProfile(userName);              
                // making search field empty
                setTimeout(() => event.target.value = '', 600);
            } else {
                showCautionAlert('No user found with the provided username.\nPlease enter correct username to search the user.');
                event.target.value = '';
            }                    
        })        
    }
})


// to show edit profile box on clicking 'edit-profile-button' button
document.getElementById('edit-profile-btn').addEventListener('click', () => {
    document.getElementById('edit-profile-box').style.display = 'block';
})


// to hide edit profile box on clicking cancel
document.getElementById('edit-profile-cancel-btn').addEventListener('click', () => {
    document.getElementById('edit-profile-box').style.display = 'none';
    removeDetailsOfEditProfile();
})


// to update the user profile as per details provided by user
document.getElementById('edit-profile-confirm-btn').addEventListener('click', () => {
    
    clearAllIntervals(); // temporarily stopping them, don't want to run a lot of things together
    const userProfileBody = {} // creating an empty dictionary
    
    // storing only those values in body which have at least 1 character    
    if (document.getElementById('edit-name-new').value.length > 0)
        userProfileBody["name"] = document.getElementById('edit-name-new').value;
    if (document.getElementById('edit-email-new').value.length > 0)
        userProfileBody["email"] = document.getElementById('edit-email-new').value;
    if (document.getElementById('edit-password-new').value.length > 0)
        userProfileBody["password"] = document.getElementById('edit-password-new').value;
        
    const fetchEditProfile = fetch('http://localhost:5000/user/', {
    method: 'PUT',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': `token ${token}`,
    },  
    body: JSON.stringify(userProfileBody),
    })
    .then((fetchEditProfileObj) => {
        if (fetchEditProfileObj.status === 200) {
            fetchEditProfileObj.json().then((result) => {
                document.getElementById('edit-profile-box').style.display = 'none';
                updateProfileDetailsUser();
                removeDetailsOfEditProfile();
                setAllIntervals(); // restarting them
            })
        } else if (fetchEditProfileObj.status === 400) {
            showErrorAlert('Malformed user object.\nIt seems that the data entered is not of correct format.');
            setAllIntervals(); // restarting them
        } else if (fetchEditProfileObj.status === 403) {
            showErrorAlert('Invalid Authorization Token.\nIt seems that you are not authorized to edit this profile.');
            setAllIntervals(); // restarting them
        }  
    })    
    .catch((error) => {
        showErrorAlert(error);
    });
})

// to show user upload post box so they can make a post
document.getElementById('upload-post-btn').addEventListener('click', () => {
    document.getElementById('upload-post-box').style.display = 'block';
})

// to hide user upload post box on clicking cancel
document.getElementById('upload-post-cancel-btn').addEventListener('click', () => {
    document.getElementById('upload-post-box').style.display = 'none';
    document.getElementById('upload-post-description-txt').value = '';
})


// to make a post with the details provide by user
document.getElementById('upload-post-confirm-btn').addEventListener('click', () => {

    clearAllIntervals(); // temporarily stopping them
    let fetchImageSrc;
    if (!document.getElementById('upload-post-image-src').files[0]) {
        showCautionAlert('Image field empty.\nPlease choose an image to upload.');
        setAllIntervals(); // restarting them
    } else {
        fetchImageSrc = fileToDataUrl(document.getElementById('upload-post-image-src').files[0]);    

        if (document.getElementById('upload-post-description-txt').value.length === 0) {
            showCautionAlert('Description field empty.\nPlease enter description of image to proceed.');
            setAllIntervals(); // restarting them
        } else if (fetchImageSrc === 'Error') {
            showErrorAlert('Provided file is not a png image.\nPlease upload png images only.');
            setAllIntervals(); // restarting them
        } else {

            fetchImageSrc.then((imageSrc) => {
                const imageBody = {
                    "description_text": document.getElementById('upload-post-description-txt').value,
                    "src": imageSrc.split(',')[1],
                };
                
                const fetchMakePost = fetch('http://localhost:5000/post/', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': `token ${token}`,
                },  
                body: JSON.stringify(imageBody),
                })
                .then((fetchMakePostObj) => {
                    if (fetchMakePostObj.status === 200) {
                        fetchMakePostObj.json().then((resultPostId) => {
                            const fetchGetPost = fetch('http://localhost:5000/post/?id=' + resultPostId.post_id, 
                            fetchMethodHeaderWithToken('GET', token))   
                            .then((fetchGetPostObj) => {
                                if (fetchGetPostObj.status === 200) {
                                    fetchGetPostObj.json().then((post) => {
                                        insertPostsOnPages(post, document.getElementById('user-profile-feed-box') ,'user');
                                    })                                    
                                } else {
                                    loadUserProfilePage();
                                    showUserProfilePage();
                                }

                            })

                            document.getElementById('upload-post-box').style.display = 'none';
                            document.getElementById('upload-post-description-txt').value = '';

                            setAllIntervals(); // restarting them                            
                        })
                    } else if (fetchMakePostObj.status == 400) {
                        showErrorAlert('Malformed request.\nImage could not be processed.');
                        setAllIntervals(); // restarting them
                    } else if (fetchMakePostObj.status == 403) {
                        showErrorAlert('Invalid Authorization Token.\nIt seems that you have provided an expired token.');
                        setAllIntervals(); // restarting them
                    } 
                })
                .catch((error) => {
                    showErrorAlert(error);
                });
            })
        }
    }
})


// to show 'Confirm deletion' message on selecting 'Delete' option on edit post box
document.getElementById('edit-post-delete-op').addEventListener('click', () => {    
    document.getElementById('delete-update-box').style.display = 'none';
    document.getElementById('delete-confirm-message').style.display = 'block';
    document.getElementById('delete-post-confirm-btn').style.display = 'block';

})

// to hide edit post box on clicking cancel
document.getElementById('edit-post-cancel-btn').addEventListener('click', () => restoreEditPostBox())

const restoreEditPostBox = () => {
    document.getElementById('edit-post-box').style.display = 'none';
    document.getElementById('delete-update-box').style.display = 'flex';
    document.getElementById('delete-confirm-message').style.display = 'none';
    document.getElementById('delete-post-confirm-btn').style.display = 'none';
}

// to delete a post as asked by the user
document.getElementById('delete-post-confirm-btn').addEventListener('click', (event) => {

    clearAllIntervals(); // temporarily stopping them
    let postID = event.target.value;

    const fetchDeletePost = fetch('http://localhost:5000/post/?id=' + postID, fetchMethodHeaderWithToken('DELETE', token))    
    .then((fetchDeletePostObj) => {
        if (fetchDeletePostObj.status === 200) {   
            showSuccessAlert('Post removed successfully.');
            restoreEditPostBox();
            document.getElementById(`user-post-box-${postID}`).remove();
            setAllIntervals(); // restarting them
        } else if (fetchDeletePostObj.status === 400) {
            showErrorAlert('Malformed request.\nPlease try again.');
            restoreEditPostBox();
            setAllIntervals(); // restarting them
        } else if (fetchDeletePostObj.status === 403) {
            showErrorAlert('Invalid Authorization Token.\nIt seems that you have provided an expired token.');
            restoreEditPostBox();
            setAllIntervals(); // restarting them
        } else if (fetchDeletePostObj.status === 404) {
            showErrorAlert('Post not found, it may have been deleted already.\nPlease refresh page and try again.');
            restoreEditPostBox();
            setAllIntervals(); // restarting them
        } 
    })
    .catch((error) => {
        showErrorAlert(error);
    });
})


// to show update post box on selecting 'Update' option on edit post box
document.getElementById('edit-post-update-op').addEventListener('click', () => {
    document.getElementById('update-post-box').style.display = 'block';
    document.getElementById('edit-post-box').style.display = 'none';
})

// to hide update post box on clicking cancel
document.getElementById('update-post-cancel-btn').addEventListener('click', () => {
    document.getElementById('update-post-box').style.display = 'none';
    document.getElementById('update-post-description-txt').value = '';
})


// to update the description of a post with the new one provided by the user
document.getElementById('update-post-confirm-btn').addEventListener('click', (event) => {

    clearAllIntervals(); // temporarily stopping them
    let postID = event.target.value;
    let postDescBody = {
        description_text: document.getElementById('update-post-description-txt').value,
    }

    const fetchEditPost = fetch('http://localhost:5000/post/?id=' + postID, {
        method: 'PUT',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `token ${token}`,
        },  
        body: JSON.stringify(postDescBody),
    })
    
    fetchEditPost.then((fetchEditPostObj) => {
        if (fetchEditPostObj.status === 200) {            
            let newPostDesc = document.getElementById('update-post-description-txt')
            document.getElementById('update-post-box').style.display = 'none';
            document.getElementById(`user-post-desc-${postID}`).innerText = newPostDesc.value;
            newPostDesc.value = '';
            showSuccessAlert('Post updated successfully.');
            setAllIntervals(); // Restarting them
        } else {
            showErrorAlert('Unable to update post description.');
            setAllIntervals(); // Restarting them
        }
    })
    .catch((error) => {
        showErrorAlert(error);
    });
})


// adding event listener to allow logged-in user to follow or unfollow any user
document.getElementById("follow-user-btn").addEventListener('click', () => {

    let followUsername = document.getElementById("other-personal-username").innerText;
    let followUserBtn = document.getElementById("follow-user-btn");

    let action = '';
    if (followUserBtn.innerText === 'Follow') 
        action = 'follow';
    else 
        action = 'unfollow';    
      
    const fetchFollowUser = fetch('http://localhost:5000/user/' + action + '?username=' + followUsername, 
                                    fetchMethodHeaderWithToken('PUT', token))
    
    .then((fetchFollowObj) => {
        if (fetchFollowObj.status === 200) {
            fetchFollowObj.json().then(result => {
                scrollHeight = 0;
                if (followUserBtn.innerText === 'Follow') {
                    // adding the other user id to the locally stored list of people following by the logged in user
                    userFollowingPeople.push(globalOtherUserId); 
                    followUserBtn.innerText = 'Unfollow';
                } else {
                    // removing the other user id from the locally stored list
                    userFollowingPeople.splice(userFollowingPeople.indexOf(globalOtherUserId), 1);
                    followUserBtn.innerText = 'Follow';
                }
                loadUserFeed(); // load home page (user feed) to reflect the correct posts only from users following
            })
        } else if (fetchFollowObj.status === 400) {
            showErrorAlert('Malformed request.\nPlease try again.');
        } else if (fetchFollowObj.status === 403) {
            showErrorAlert('Invalid Authorization Token.\nIt seems that you have provided an expired token.');
        } else if (fetchFollowObj.status === 404) {
            showErrorAlert('User not found.\nPlease enter the correct username of the person.');
        } 
    })
    .catch((error) => {
        showErrorAlert(error);
    });
})


// 2ND PART STARTS FROM HERE
// In the 2nd part, I have defined function to load post, likes and comments on all pages.


// adding event to like button using this function
const addEventLikePost = (event, page) => {

    let postID = event.target.id.split('-')[3];

    // if button is Like, we will call fetch to like this post
    if (event.target.innerText === 'Like'){
        event.target.innerText = 'Unlike';

        const likesPostFetch = fetch('http://localhost:5000/post/like?id='+ postID, fetchMethodHeaderWithToken('PUT', token))
        likesPostFetch.then((likePost) =>{
            if (likePost.status !== 200) {
                event.target.innerText = 'Like';
                showErrorAlert('Error in liking the post');
            } else if (likePost.status === 200) {
                event.target.innerText = 'Unlike';
            }
        })
        .catch((error) => {
            showErrorAlert(error);
        });

    } else { // else if button is Unlike, we will call fetch to unlike this post
        event.target.innerText = 'Like';
        const unlikePostFetch = fetch('http://localhost:5000/post/unlike?id='+ postID, fetchMethodHeaderWithToken('PUT', token))
        unlikePostFetch.then((unlikePost) =>{
            if (unlikePost.status !== 200) {
                event.target.innerText = 'Unlike';
                showErrorAlert('Error in unliking the post');
            } else if (unlikePost.status === 200) {
                event.target.innerText = 'Like';
            }
        })
        .catch((error) => {
            showErrorAlert(error);
        });
    }
}

// adding event to comment button using this function
const addEventCommentOnPost = (event, page) => {
                            
    //checking if enter key is pressed and comment text input is non empty
    if (event.key === 'Enter' && event.target.value.length > 0) {
    
        const commentBody = {
            "comment": event.target.value,
        };
    
        let postID = event.target.id.split('-')[3]
    
        // calling fetch to post this comment                            
        const postCommentFetch = fetch('http://localhost:5000/post/comment?id='+ postID, {
            method: 'PUT',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': `token ${token}`,
            },  
            body: JSON.stringify(commentBody),
        })
        postCommentFetch.then((postCommentObj) => {
            if (postCommentObj.status !== 200) {
                showErrorAlert('Unable to post comment.\nPlease try again.')
            } else if (postCommentObj.status === 200) {   
                // finally setting comment text field to empty value
                event.target.value = '';
            }
        })
        .catch((error) => {
            showErrorAlert(error);
        });
    }
}


// regular running function to live update likes on user main and other user pages
const liveUpdateLikes = () => {

    // to check for comments difference
    let likesCountButtons = document.querySelectorAll('.user-likes-count-btn');

    likesCountButtons.forEach((likesCountBtn) => {

        let postID = likesCountBtn.id.split('-')[4];

        const fetchPost = fetch(`http://localhost:5000/post/?id=${postID}`, fetchMethodHeaderWithToken('GET', token))
        .then((fetchPostObj) => {
            if (fetchPostObj.status === 200) {
                fetchPostObj.json().then((post) => {

                    // only proceed when setInterval is running, i.e, when user is logged in
                    if(intervalLiveUpdateLikes && (document.getElementById(`user-likes-count-btn-${post.id}`))) { 

                        // to check for likes difference
                        let likesCount = parseInt(document.getElementById(`user-likes-count-btn-${post.id}`).innerText.split(' ')[1]);

                        if (likesCount !== post.meta.likes.length) {                            
                            const likesBox = document.getElementById(`user-likes-popup-${post.id}`);                            
                            document.getElementById(`user-likes-count-btn-${post.id}`).innerText = `Likes: ${post.meta.likes.length}`;
                            insertLikesOnPosts(post, likesBox, 'user');
                        }

                    }
                })
            }
        })
    })
}


// regular running function to live update comments on user main and other user pages
const liveUpdateComments = () => {

    // to check for comments difference
    let commentsCountButtons = document.querySelectorAll('.user-comments-count-btn');

    commentsCountButtons.forEach((commentsCountBtn) => {

        let postID = commentsCountBtn.id.split('-')[4];

        const fetchPost = fetch(`http://localhost:5000/post/?id=${postID}`, fetchMethodHeaderWithToken('GET', token))
        .then((fetchPostObj) => {
            if (fetchPostObj.status === 200) {
                fetchPostObj.json().then((post) => {

                    const commentsBox = document.getElementById(`user-comments-show-box-${post.id}`);
                    // only proceed when setInterval is running, i.e, when user is logged in
                    if(intervalLiveUpdateComments && commentsBox) { 
                        
                        if (post.comments.length > (commentsBox.childElementCount/2)) { // only update in case of a mismatch

                            while (commentsBox.firstChild) {
                                commentsBox.removeChild(commentsBox.lastChild);
                            }
                            document.getElementById(`user-comments-count-btn-${post.id}`).innerText = `Comments: ${post.comments.length}`;
                            insertCommentsOnPosts(post, commentsBox, 'user');                        
                        }
                    }
                })
            }
        })
    })
}


// to update likes and comments for the home page (user feed)
const liveUpdateUserFeed = () => {

    const fetchUserFeed = fetch(`http://localhost:5000/user/feed?p=0&n=${feedPostsStart}`, fetchMethodHeaderWithToken('GET', token))
    .then((fetchObject) => {
        if (fetchObject.status === 200) {
            fetchObject.json().then(allPosts => { 
                
                // for each post, calling function to insert that post on home (user feed) of user
                allPosts.posts.forEach((post) => {

                    if (intervalLiveUpdateUserFeed) { // only proceed if set interval is running, i.e., when user is logged in

                        // to check for comments difference
                        let commentsBox = document.getElementById(`home-comments-show-box-${post.id}`);

                        if (commentsBox) { // only checks if element is found (because sometimes post gets removed from DOM)

                            if (post.comments.length > (commentsBox.childElementCount/2)) {

                                while (commentsBox.firstChild) {
                                    commentsBox.removeChild(commentsBox.lastChild);
                                }
                                document.getElementById(`home-comments-count-btn-${post.id}`).innerText = `Comments: ${post.comments.length}`;
                                insertCommentsOnPosts(post, commentsBox, 'home');                            
                            }
                        }

                        // to check for likes difference
                        let likesBox = document.getElementById(`home-likes-popup-${post.id}`);

                        if (likesBox) { // only checks if element is found (because sometimes post gets removed from DOM)
                            let likesCount = parseInt(document.getElementById(`home-likes-count-btn-${post.id}`).innerText.split(' ')[1]);

                            if (likesCount !== post.meta.likes.length) {
                                document.getElementById(`home-likes-count-btn-${post.id}`).innerText = `Likes: ${post.meta.likes.length}`;
                                insertLikesOnPosts(post, likesBox, 'home');                            
                            }
                        }
                    }

                });
            })                      
        }
    })    
    .catch((error) => {
        console.log('Error: ', error);
    });
}


// to populate likes for a post
const insertLikesOnPosts = (post, parentElement, page) => {

    // checking if this post has any like or not and displaying data accordingly
    if (post.meta.likes.length === 0){
        parentElement.firstChild.innerText = 'No Likes yet';
        while(parentElement.lastChild.firstChild) {
            parentElement.lastChild.removeChild(parentElement.lastChild.lastChild);
        }
    } else {
        parentElement.firstChild.innerText = 'Liked by:';
    }

    let loopIndex = -1;
    const usernamesBox = document.createElement('div');
    // calling fetch to get the names for all the IDs of people who liked this post
    post.meta.likes.forEach((userId) => {
        loopIndex += 1;

        const likedByUser = fetch('http://localhost:5000/user/?id='+userId, fetchMethodHeaderWithToken('GET', token))
        .then((dataLikedByUser) => {
            if (dataLikedByUser.status !== 200) {
                showErrorAlert('User not found to show likes for a post.');
            } else if (dataLikedByUser.status === 200) {
                dataLikedByUser.json().then(likedByUserName => {
                    let likedByUser = document.createElement('div');
                    usernamesBox.appendChild(likedByUser);
                    likedByUser.innerText = likedByUserName.username;
                    likedByUser.className = `post-liked-by-username`;
                    likedByUser.id = `${page}-${post.id}-liked-by-${likedByUserName.username}`;

                    // adding event to open profile of the user who liked the post
                    likedByUser.addEventListener('click', (event) => {
                        loadProfile(event.target.innerText);
                    })

                    if (loopIndex === (post.meta.likes.length-1) ) {
                        parentElement.removeChild(parentElement.lastChild);
                        parentElement.appendChild(usernamesBox);
                    }
                })
            }
        })                                         
    })       
}


// to populate comments on a post
const insertCommentsOnPosts = (post, parentElement, page) => {   
    // populating all the comments for this post
    for (var c=0; c<post.comments.length; c++){
        const commentAuthorDateBox = document.createElement('div');
        commentAuthorDateBox.className = 'comment-author-date-box';
        parentElement.appendChild(commentAuthorDateBox);

        const commentAuthor = document.createElement('div');
        const commentDate = document.createElement('div');

        commentAuthorDateBox.appendChild(commentAuthor);
        commentAuthorDateBox.appendChild(commentDate);
        commentAuthor.className = 'comment-author';

        // adding event to open profile of the user who posted the comment
        commentAuthor.addEventListener('click', (event) => {
            loadProfile(event.target.innerText);
        })
        
        commentDate.className = 'comment-date';

        commentAuthor.innerText = post.comments[c].author;        
        commentDate.innerText = convertUnixToDate(post.comments[c].published);

        const commentData = document.createElement('div');
        parentElement.appendChild(commentData);
        commentData.innerText = post.comments[c].comment;
    }
}


// to populate posts on any page of a user, this same function is used to populate posts on all 3 pages
const insertPostsOnPages = (post, parentElement, page) => {                
       
    let pageType = page;
    if (page === 'other') {
        page = 'user';
    }
    // creating a box to store each post and appending it to main post box (parentElement) of the page provided
    const postBox = document.createElement('div');
    postBox.className = 'post-box';
    postBox.id = `${page}-post-box-${post.id}`;
    parentElement.appendChild(postBox);

    // create box to store post author name and date/time
    const postAuthorDate = document.createElement('div');
    postBox.appendChild(postAuthorDate);
    postAuthorDate.className = 'post-author-box';

    const postAuthor = document.createElement('div');
    postAuthor.className = 'post-author';
    postAuthor.id = `${page}-${post.id}-${post.meta.author}`;

    // adding event to open profile of the user who posted the image
    postAuthor.addEventListener('click', (event) => {
        loadProfile(event.target.id.split('-')[2]);
    })

    const postDate = document.createElement('div');
    postDate.className = 'post-date';

    postAuthorDate.appendChild(postAuthor);
    postAuthorDate.appendChild(postDate);

    postAuthor.innerText = post.meta.author;    
    postDate.innerText = convertUnixToDate(post.meta.published); // convert date from unix to required format

    // create box to store post description and post edit button
    const postDescBox = document.createElement('div');
    postBox.appendChild(postDescBox);
    postDescBox.className = 'post-desc-box';

    const postDescription = document.createElement('div');
    postDescription.className = 'post-desc';
    postDescription.id = `${page}-post-desc-${post.id}`;
    postDescBox.appendChild(postDescription);
    postDescription.innerText = post.meta.description_text;

    // create post edit button only for user profile pages
    if (pageType === 'user') {
        const postEditDescBtn = document.createElement('button');
        postEditDescBtn.className = 'post-edit-btn';
        postEditDescBtn.id = `${page}-post-edit-btn-${post.id}`;
        postDescBox.appendChild(postEditDescBtn);
        postEditDescBtn.innerText = 'Edit';
        postEditDescBtn.addEventListener('click', (event) => {
            let editPostID = event.target.id.split('-')[4];
            document.getElementById('edit-post-box').style.display = 'block';
            // attaching post ID and details to button so that when user clicks on confirm, these can be sent in fetch call
            let postDescToBeEdited = document.getElementById(`user-post-desc-${editPostID}`);            
            document.getElementById('edit-post-old-desc').innerText = postDescToBeEdited.innerText
            document.getElementById('update-post-old-desc').innerText = postDescToBeEdited.innerText
            document.getElementById('update-post-confirm-btn').value = editPostID;
            document.getElementById('delete-post-confirm-btn').value = editPostID;
        });
    }

    // create images
    const postImage = document.createElement('div');
    postImage.className = 'post-image-box';
    postBox.appendChild(postImage);

    const postShowImage = document.createElement('img');
    postShowImage.setAttribute('src', `data:image/jpeg;base64,${post.src}`);
    postShowImage.alt = `Image for a post by ${post.meta.author}`;
    postImage.appendChild(postShowImage);

    // create box to show likes and comment buttons
    const postLikesComments = document.createElement('div');
    postLikesComments.className = 'likes-count-box';
    postBox.appendChild(postLikesComments);
    
    const postLikesCount = document.createElement('button');
    postLikesCount.className = page+'-likes-count-btn';
    postLikesCount.id = `${page}-likes-count-btn-${post.id}`;

    const postCommentsCount = document.createElement('button');
    postCommentsCount.className = page+'-comments-count-btn';
    postCommentsCount.id = `${page}-comments-count-btn-${post.id}`;

    // adding event to show all comments for a post on a click
    postCommentsCount.addEventListener('click', (event) => addEventShowComments(event, page))

    postLikesComments.appendChild(postLikesCount);
    postLikesComments.appendChild(postCommentsCount);

    postLikesCount.innerText = `Likes: ${post.meta.likes.length}`;
    postCommentsCount.innerText = `Comments: ${post.comments.length}`;
    
    // create popups to show names of people who liked the post
    const likesPopUpBox = document.createElement('div');
    likesPopUpBox.className = 'likes-popup-box';
    postBox.appendChild(likesPopUpBox);

    const likesPopUp = document.createElement('div');
    likesPopUp.className = 'likes-popup';                     
    likesPopUpBox.appendChild(likesPopUp);                     
    likesPopUp.id = `${page}-likes-popup-${post.id}`;   
    
    const likesPopupMessage = document.createElement('div');
    likesPopUp.appendChild(likesPopupMessage);

    const likesPopupNamesBox = document.createElement('div');
    likesPopUp.appendChild(likesPopupNamesBox);
    
    insertLikesOnPosts(post, likesPopUp, page);

    // adding event to likes show button
    postLikesCount.addEventListener('click', (event) => addEventShowLikes(event, page))

    const postLikeOrComment = document.createElement('div');
    postBox.appendChild(postLikeOrComment);
    postLikeOrComment.className = 'like-box';

    const postLike = document.createElement('button');
    postLike.className = 'like-btn';
    postLike.id = `${page}-like-btn-${post.id}`;     
    
    postLike.addEventListener('click', (event) => addEventLikePost(event, page))

    const postComment = document.createElement('button');
    postComment.className = 'comment-btn';
    postComment.id = `${page}-comment-btn-${post.id}`;       
    
    // adding event to show all comments for a post on a click
    postComment.addEventListener('click', (event) => addEventShowComments(event, page))

    postLikeOrComment.appendChild(postLike);
    postLikeOrComment.appendChild(postComment);

    // to check if this post is liked by user or not, and show Like/Unlike button accordingly
    if (post.meta.likes.includes(loginUserId)){
        postLike.innerText = 'Unlike';
    } else {
        postLike.innerText = 'Like';
    }
    postComment.innerText = 'Comment';

    // creating box to store text field to post comments
    const postACommentBox = document.createElement('div');
    postACommentBox.className = 'comment-write-box';
    postACommentBox.id = `${page}-comment-write-box-${post.id}`;
    postBox.appendChild(postACommentBox);

    // creating text field to write a comment
    const postCommentText = document.createElement('INPUT');
    postCommentText.setAttribute("type", "text");
    postCommentText.setAttribute("placeholder", "Write a comment... press Enter to post!");
    postCommentText.className = 'comment-text';
    postCommentText.id = `${page}-comment-text-${post.id}`;
    postACommentBox.appendChild(postCommentText);

    // adding event to allow user to comment on a post
    postCommentText.addEventListener('keyup', (event) => addEventCommentOnPost(event, page))

    const postComments = document.createElement('div');
    postComments.className = 'comments-show-box';
    postComments.id = `${page}-comments-show-box-${post.id}`;
    postBox.appendChild(postComments);

    insertCommentsOnPosts(post, postComments, page); // to insert all comments for this post
}


// 3RD PART STARTS FROM HERE
// In the 3rd part, I have defined functions to check what user is doing, where he is and which pages to load/show.


// to check if user scrolled to bottom of page to load more posts
const checkScrollToBottom = () => {
    if ( currentPage === 'Home' && window.scrollY > (document.body.scrollHeight - window.innerHeight) - 500) {
        if (userHasAnyFeed > 0) {
            clearInterval(intervalCheckBottom);
            loadMoreUserFeedPosts();      
            setTimeout(() => {intervalCheckBottom = setInterval(checkScrollToBottom, 4000);}, 2000)  
        }
        
    }
}


// to show feed for a user
const loadUserFeed = () => {

    // remove old elements from home page (user feed) before populating all correct elements
    let userFeedBox = document.getElementById('user-feed-box'); // to remove all posts
    while (userFeedBox.firstChild) {
        userFeedBox.removeChild(userFeedBox.lastChild);
    } 
   
    feedPostsStart = 0;
    const fetchUserFeed = fetch(`http://localhost:5000/user/feed?p=${feedPostsStart}&n=${feedLength}`, 
    fetchMethodHeaderWithToken('GET', token))
    .then((data) => {
        if (data.status === 403) {
            showErrorAlert('Unable to get user feed.\nPlease try again.')
        } else if (data.status === 200) {
            data.json().then(result => {                  

                if (result.posts.length > 0) {
                    userHasAnyFeed = 1;
                    document.getElementById('new-user-message').style.display = 'none';
                    feedPostsStart += result.posts.length; // to increment count of next start array by number of posts got
                } else {
                    loadNewUserMessage(document.getElementById('new-user-message'));                    
                    document.getElementById('new-user-message').style.display = 'block';
                }
                // for each post, calling function to insert that post on home (user feed) of user
                result.posts.forEach((post) => {
                    insertPostsOnPages(post, document.getElementById('user-feed-box'), 'home');
                    // scroll to top of window
                    window.scrollTo(0,0); 
                })
                
                setAllIntervals();
            })                      
        }
    })    
    .catch((error) => {
        console.log('Error: ', error);
    });
}

// infinite scroll has been implemented using this function
const loadMoreUserFeedPosts = () => {
    
    const fetchUserFeed = fetch(`http://localhost:5000/user/feed?p=${feedPostsStart}&n=${feedLength}`, 
    fetchMethodHeaderWithToken('GET', token))
    .then((data) => {
        if (data.status === 403) {
            showErrorAlert('Unable to get user feed.\nPlease try again.')
        } else if (data.status === 200) {
            data.json().then(result => {   
                if (result.posts.length > 0) {
                    feedPostsStart += result.posts.length; // to increment count of next start array by number of posts got
                }
                // for each post, calling function to insert that post on home (user feed) of user
                result.posts.forEach((post) => insertPostsOnPages(post, document.getElementById('user-feed-box'), 'home'))
            })                      
        }
    })   
}


// to load the profile page of the logged in user with all elements and details
const loadUserProfilePage = () => {

    // remove old elements from user profile page before populating all correct elements
    let userFollowingBox = document.getElementById('user-personal-following-box'); // to remove names of following people
    while (userFollowingBox.firstChild) {
        userFollowingBox.removeChild(userFollowingBox.lastChild);
    }

    let userFeedBox = document.getElementById('user-profile-feed-box'); // to remove all posts
    while (userFeedBox.firstChild) {
        userFeedBox.removeChild(userFeedBox.lastChild);
    }    

    // calling fetch Get /user/ to get and store the user ID and full name for this user as it will be required later
    const fetchGetUser = fetch('http://localhost:5000/user/', fetchMethodHeaderWithToken('GET', token))
    
    fetchGetUser.then((fetchGetUserObj) => {
        if (fetchGetUserObj.status !== 200) {
            showErrorAlert('Unable to load user profile.\nPlease try again.')
        } else if (fetchGetUserObj.status === 200) {
            fetchGetUserObj.json().then((getUserDetails) => {
                // store user ID and Name for this user to be used further
                loginUserId = getUserDetails.id;
                loginUsername = getUserDetails.username;

                getLastPostID(); // it is run as part of getting new post notifications 

                // populating elements of user profile page
                document.getElementById("user-personal-message").innerText = `Hello ${getUserDetails.name}!`;
                document.getElementById("user-personal-username").innerText = getUserDetails.username;
                document.getElementById("user-personal-name").innerText = getUserDetails.name;
                document.getElementById("user-personal-email").innerText = getUserDetails.email;
                document.getElementById("user-personal-followed-by").innerText = `${getUserDetails.followed_num} people`;
                document.getElementById("user-personal-following").innerText = `${getUserDetails.following.length} people`;

                // fetching names of people "following" from their IDs and populating in the profile page
                getUserDetails.following.forEach((userFollowingId) => {
                    userFollowingPeople.push(userFollowingId); // to keep track of all the users followed by logged in user
                    const fetchUserFollowing = fetch('http://localhost:5000/user/?id='+ userFollowingId, 
                    fetchMethodHeaderWithToken('GET', token))

                    fetchUserFollowing.then((fetchUserObj) => {
                        if (fetchUserObj.status === 200) {
                            fetchUserObj.json().then((userFollowingName) => {
                                let userNameElement = document.createElement('div');
                                userNameElement.innerText = userFollowingName.username;
                                document.getElementById('user-personal-following-box').appendChild(userNameElement);
                            })
                        }
                    })
                });

                // fetching all posts made by this user from their post IDs and adding to the DOM
                getUserDetails.posts.forEach((userPostID) => {
                    const fetchUserPosts = fetch('http://localhost:5000/post/?id='+ userPostID, 
                    fetchMethodHeaderWithToken('GET', token))

                    fetchUserPosts.then((fetchUserPostsObj) => {
                        if (fetchUserPostsObj.status !== 200) {
                            showErrorAlert('No post found for user profile page.\nPlease try again.')
                        } else if (fetchUserPostsObj.status === 200) {
                            fetchUserPostsObj.json().then((userPost) => {
                                insertPostsOnPages(userPost, document.getElementById('user-profile-feed-box'), 'user')                                
                            })
                        }
                    })
                });
            })
        }
    })
}


// load other user profile page
const loadOtherUserProfilePage = (otherUsername) => {

    // remove old elements from other user profile page before populating all correct elements
    let otherFollowingBox = document.getElementById('other-personal-following-box'); // to remove names of following people
    while (otherFollowingBox.firstChild) {
        otherFollowingBox.removeChild(otherFollowingBox.lastChild);
    }

    let otherFeedBox = document.getElementById('other-profile-feed-box'); // to remove all posts
    while (otherFeedBox.firstChild) {
        otherFeedBox.removeChild(otherFeedBox.lastChild);
    }

    // now show the page with all correct elements after a small delay, allowing old elements to clear
    setTimeout(() => {
        showOtherUserProfilePage();
        window.scrollTo(0,0); // scroll to top of window
    }, 1400);

    // calling fetch Get /user/ to get and store the user ID and full name for this user as it will be required later
    const fetchGetUser = fetch('http://localhost:5000/user/?username='+ otherUsername, fetchMethodHeaderWithToken('GET', token))
    
    fetchGetUser.then((fetchGetUserObj) => {
        if (fetchGetUserObj.status !== 200) {
            showErrorAlert('User not found.\nPlease try again.')
        } else if (fetchGetUserObj.status === 200) {
            fetchGetUserObj.json().then((getUserDetails) => {

                // populating elements of other user profile page
                document.getElementById("other-personal-message").innerText = `${getUserDetails.name}`;
                document.getElementById("other-personal-username").innerText = getUserDetails.username;
                document.getElementById("other-personal-name").innerText = getUserDetails.name;
                document.getElementById("other-personal-email").innerText = getUserDetails.email;
                document.getElementById("other-personal-followed-by").innerText = `${getUserDetails.followed_num} people`;
                document.getElementById("other-personal-following").innerText = `${getUserDetails.following.length} people`;
            
                globalOtherUserId = getUserDetails.id; // storing so that when we need it for (un)follow, we don't need to fetch again

                // checking if this user is being followed by logged-in user and showing follow/unfollow button accordingly
                if (userFollowingPeople.includes(getUserDetails.id)) {
                    document.getElementById("follow-user-btn").innerText = 'Unfollow';
                } else {
                    document.getElementById("follow-user-btn").innerText = 'Follow';
                }    

                // fetching all posts made by this user from their post IDs and adding to the DOM
                getUserDetails.posts.forEach((userPostID) => {
                    const fetchUserPosts = fetch('http://localhost:5000/post/?id='+ userPostID, 
                    fetchMethodHeaderWithToken('GET', token))

                    fetchUserPosts.then((fetchUserPostsObj) => {
                        if (fetchUserPostsObj.status !== 200) {
                            showErrorAlert('No post found for users public page.\nPlease try again.')
                        } else if (fetchUserPostsObj.status === 200) {
                            fetchUserPostsObj.json().then((userPost) => {
                                insertPostsOnPages(userPost, document.getElementById('other-profile-feed-box'), 'other')                                
                            })
                        }
                    })
                });
            })
        }
    })
}


// show login window
const showLoginWindow = () => {
    currentPage = 'Login';
    document.getElementById('login-window').style.display = 'block';
    document.getElementById('registration-window').style.display = 'none'; 
    document.getElementById('home-feed-btn').style.display = 'none';      
    document.getElementById('user-profile-btn').style.display = 'none';      
    document.getElementById('search-user').style.display = 'none';  
    document.getElementById('logout-btn').style.display = 'none';  
    document.getElementById('user-feed-box').style.display = 'none';    
    document.getElementById('user-profile-page').style.display = 'none';
    document.getElementById('other-profile-page').style.display = 'none';
}


// show registration window
const showRegistrationWindow = () => {
    currentPage = 'Register';
    document.getElementById('login-window').style.display = 'none';
    document.getElementById('registration-window').style.display = 'block';     
    document.getElementById('home-feed-btn').style.display = 'none';      
    document.getElementById('user-profile-btn').style.display = 'none';      
    document.getElementById('search-user').style.display = 'none';  
    document.getElementById('logout-btn').style.display = 'none';   
    document.getElementById('user-feed-box').style.display = 'none';    
    document.getElementById('user-profile-page').style.display = 'none';
    document.getElementById('other-profile-page').style.display = 'none';
}


// to show user feed for the user
const showUserFeed = () => {

    hideAllLikePopups(); // to hide all like popups on page load

    if (userHasAnyFeed === 0) {
        document.getElementById('new-user-message').style.display = 'block';
    }
    document.getElementById('login-window').style.display = 'none';
    document.getElementById('registration-window').style.display = 'none'; 

    document.getElementById('home-feed-btn').style.display = 'block';  
    document.getElementById('home-feed-btn').style.backgroundColor = '#2883bf'; // highlighting this button
    document.getElementById('home-feed-btn').style.color = '#f7f9fa'; 

    document.getElementById('user-profile-btn').style.display = 'block';  
    document.getElementById('user-profile-btn').style.backgroundColor = '#f7f9fa';  
    document.getElementById('user-profile-btn').style.color = '#000000'; 

    document.getElementById('search-user').style.display = 'block';  
    document.getElementById('logout-btn').style.display = 'block';    
    document.getElementById('user-feed-box').style.display = 'block';
    document.getElementById('user-profile-page').style.display = 'none';
    document.getElementById('other-profile-page').style.display = 'none';

    document.getElementById('edit-profile-box').style.display = 'none';
    removeDetailsOfEditProfile();
    document.getElementById('edit-post-box').style.display = 'none';
    restoreEditPostBox();
    document.getElementById('update-post-box').style.display = 'none';
    document.getElementById('upload-post-box').style.display = 'none';
    document.getElementById('upload-post-description-txt').value = '';

    // scroll to top or some other part of user feed, depending on from which page you are coming from
    // if you are on home page, then this will take you to top
    // otherwise if you move from home to other page, we will store the scroll height and when you comes back,
    // we will show the page at that specific spot only
    if (currentPage === 'Home') {
        window.scrollTo(0,0); 
    } else {
        window.scrollTo(0,scrollHeight); 
    }  
    currentPage = 'Home';
}


// to show logged in user's profile page
const showUserProfilePage = () => {

    hideAllLikePopups(); // to hide all like popups on page load

    // saves height location of user feed page
    if (currentPage === 'Home') {
        scrollHeight = window.scrollY;
    }

    // scroll to top of window
    window.scrollTo(0,0); 

    currentPage = 'User';

    document.getElementById('new-user-message').style.display = 'none';
    document.getElementById('login-window').style.display = 'none';
    document.getElementById('registration-window').style.display = 'none'; 
    
    document.getElementById('home-feed-btn').style.display = 'block';  
    document.getElementById('home-feed-btn').style.backgroundColor = '#f7f9fa'; 
    document.getElementById('home-feed-btn').style.color = '#000000'; 
    
    document.getElementById('user-profile-btn').style.display = 'block';  
    document.getElementById('user-profile-btn').style.backgroundColor = '#2883bf'; // highlighting this button
    document.getElementById('user-profile-btn').style.color = '#f7f9fa'; 
    
    document.getElementById('search-user').style.display = 'block';  
    document.getElementById('logout-btn').style.display = 'block';  
    document.getElementById('user-feed-box').style.display = 'none';    
    document.getElementById('user-profile-page').style.display = 'block';
    document.getElementById('other-profile-page').style.display = 'none';
}


// to show public profiles of other users
const showOtherUserProfilePage = () => {

    hideAllLikePopups(); // to hide all like popups on page load

    // saves height location of user feed page
    if (currentPage === 'Home') {
        scrollHeight = window.scrollY;
    }
    
    // scroll to top of window
    window.scrollTo(0,0); 

    currentPage = 'Other';

    document.getElementById('new-user-message').style.display = 'none';
    document.getElementById('login-window').style.display = 'none';
    document.getElementById('registration-window').style.display = 'none'; 
    
    document.getElementById('home-feed-btn').style.display = 'block';  
    document.getElementById('home-feed-btn').style.backgroundColor = '#f7f9fa'; 
    document.getElementById('home-feed-btn').style.color = '#000000';  
    
    document.getElementById('user-profile-btn').style.display = 'block';  
    document.getElementById('user-profile-btn').style.backgroundColor = '#f7f9fa';  
    document.getElementById('user-profile-btn').style.color = '#000000'; 
    
    document.getElementById('search-user').style.display = 'block';  
    document.getElementById('logout-btn').style.display = 'block';  
    document.getElementById('user-feed-box').style.display = 'none';    
    document.getElementById('user-profile-page').style.display = 'none';
    document.getElementById('other-profile-page').style.display = 'block';

    document.getElementById('edit-profile-box').style.display = 'none';
    removeDetailsOfEditProfile();
    document.getElementById('edit-post-box').style.display = 'none';
    restoreEditPostBox();
    document.getElementById('update-post-box').style.display = 'none';
    document.getElementById('upload-post-box').style.display = 'none';
    document.getElementById('upload-post-description-txt').value = '';
}


// function to load profile of main user or any other user
const loadProfile = (username) => {
    clearAllIntervals();
    if (username === loginUsername){
        showUserProfilePage();
    } else {
        loadOtherUserProfilePage(username);
    }        
    setTimeout(setAllIntervals, 2500); // to allow other pages to load
}


// load the initial pages on sign-in or page refresh
const loadPagesOnRefresh = () => { 
    loadUserProfilePage();   
    loadUserFeed();   
    // scroll to top of window
    window.scrollTo(0,0); 
}


// to set all intervals to run regulaer functions
const setAllIntervals = () => {
    if (!intervalLiveUpdateUserFeed) {
        intervalCheckBottom = setInterval(checkScrollToBottom, 2000);
        intervalLiveUpdateUserFeed = setInterval(liveUpdateUserFeed, 800);    
        intervalLiveUpdateComments = setInterval(liveUpdateComments, 1000);       
        intervalLiveUpdateLikes =  setInterval(liveUpdateLikes, 1000);  
    }
}


// to clear all intervals to run regulaer functions
const clearAllIntervals = () => {
    clearInterval(intervalCheckBottom);
    clearInterval(intervalLiveUpdateUserFeed);
    clearInterval(intervalLiveUpdateComments);
    clearInterval(intervalLiveUpdateLikes); 
    intervalLiveUpdateUserFeed = 0;
    intervalLiveUpdateComments = 0;
    intervalLiveUpdateLikes = 0;
    intervalCheckBottom = 0;
}


// to show the pages accordingly
const loadHashPages = () => {
    let enteredURL = location.hash;
    if (enteredURL.length === 0) {
        showUserFeed(); 
    } else if (enteredURL === '#profile=me') {
        showUserProfilePage();
    } else if (enteredURL === '#feed') {
        showUserFeed();    
    } else if (enteredURL !== '#profile=me' && enteredURL.substr(0,9) === '#profile=') {
        loadProfile(enteredURL.substring(9));            
    } else {
        showUserFeed(); 
    }
}


// on refresh, check if the user is logged in or not and load the pages required
if (document.cookie === 'false') {
    clearAllIntervals();
    showLoginWindow();   
} else {
    token = document.cookie;
    showNothing();
    loadPagesOnRefresh();
    loadHashPages();
}


// for mobile responsiveness, to change header elements value
window.addEventListener("resize", () => {
    //console.log(window.innerWidth);
    if (window.innerWidth < 475) {
        document.getElementById('search-user').placeholder = 'Search user...';
        document.getElementById('home-feed-btn').innerText = 'Home Page';        
    }
    if (window.innerWidth >= 475) {
        document.getElementById('search-user').placeholder = 'Search any user...';
        document.getElementById('home-feed-btn').innerText = 'Home';        
    }
});

// to turn on and off all intervals depending upon network availability
window.addEventListener('online', () => {
    setAllIntervals();
});
window.addEventListener('offline', () => {
    clearAllIntervals();
});


// to gets post id of the last post made in the database
const getLastPostID = () => {

    if (document.cookie !== 'false') { // only runs when user is logged in

        const fetchUser = fetch(`http://localhost:5000/user/?id=${checkUserId}`, fetchMethodHeaderWithToken('GET', token))
        .then((fetchUserObj) => {
            if (fetchUserObj.status === 200) {
                fetchUserObj.json().then((user) => {
                    user.posts.forEach((postID) => {
                        if (postID > lastPostId)
                            lastPostId = postID;
                    })
                    checkUserId += 1;
                    getLastPostID(); // checks if next post exists or not
                })
            } else if (fetchUserObj.status === 404) { // finally found the last post id
                lastPostId += 1;
                intervalPostNotify = setInterval(checkForNewPosts, 10000);
            }
        })    
    }
}

// regular running function to check if any new post has been made in the database
const checkForNewPosts = () => {

    if (userFollowingPeople.length > 0) { // runs only when user is following anyone    
        // try to get the post referenced by last post id
        const fetchPost = fetch(`http://localhost:5000/post/?id=${lastPostId}`, fetchMethodHeaderWithToken('GET', token))
        .then((fetchPostObj) => {
            if (fetchPostObj.status === 200) {
                fetchPostObj.json().then((post) => {
                    lastPostId += 1; // to check for next post id next time
                    let userName = post.meta.author;

                    //gets the user who made this new post to get user id
                    const fetchUser = fetch(`http://localhost:5000/user/?username=${userName}`, fetchMethodHeaderWithToken('GET', token))
                    .then((fetchUserObj) => {
                        if (fetchUserObj.status === 200) {
                            fetchUserObj.json().then((user) => {
                                let userID = user.id;
                                if (userFollowingPeople.includes(userID)) { // checks if user id is in the list of following people
                                    document.getElementById('caution-popup-heading').innerText = 'User Notification';
                                    document.getElementById('caution-popup-message').style.color = '#3464eb'; // blue shade 
                                    showCautionAlert(`${user.username} has just made a new post!!!\nYou may refresh the page and check it out.`);
                                }
                            })
                        }
                    })
                })
            }
        })   
    } 
}
