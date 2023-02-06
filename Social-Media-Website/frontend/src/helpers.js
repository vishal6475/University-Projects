/**
 * Given a js file object representing a jpg or png image, such as one taken
 * from a html file input element, return a promise which resolves to the file
 * data as a data url.
 * More info:
 *   https://developer.mozilla.org/en-US/docs/Web/API/File
 *   https://developer.mozilla.org/en-US/docs/Web/API/FileReader
 *   https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
 * 
 * Example Usage:
 *   const file = document.querySelector('input[type="file"]').files[0];
 *   console.log(fileToDataUrl(file));
 * @param {File} file The file to be read.
 * @return {Promise<string>} Promise which resolves to the file as a data url.
 */

// to get months from date
const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];


export function fileToDataUrl(file) {
    
    const validFileTypes = [ 'image/png' ]
    const valid = validFileTypes.find(type => type === file.type);
    // If the file is not png, return error and it will be handled in main.js file
    if (!valid) {
        return ('Error');
    }    
    
    const reader = new FileReader();
    reader.readAsDataURL(file);
    
    const dataUrlPromise = new Promise((resolve,reject) => {
        reader.onerror = reject;
        reader.onload = () => resolve(reader.result);
    });
    
    return dataUrlPromise;  
}


// convert date from unix to desired format
export function convertUnixToDate(unixDate) {
    let getDate = new Date(unixDate * 1000);
    return `${months[getDate.getMonth()]} ${getDate.getDay()} ${getDate.getFullYear()} ${getDate.getHours()}:${getDate.getMinutes()}`;
}


// function to set the method and token for a fetch call 
export function fetchMethodHeaderWithToken(method, token) {
    let fetchMethodHeader = {
        method: method,
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `token ${token}`,
        },
    };
    return(fetchMethodHeader);
}


// to hide all like pages, will be used when any page is loaded
export function hideAllLikePopups() {
    let allLikesPopUp = document.querySelectorAll('.likes-popup');
    allLikesPopUp.forEach((likesPopup) => {
        likesPopup.style.visibility = 'hidden';
    })
}

export function updateProfileDetailsUser() {

    // updating only those values in body which have at least 1 character    
    if (document.getElementById('edit-name-new').value.length > 0)
        document.getElementById('user-personal-name').innerText = document.getElementById('edit-name-new').value;
    if (document.getElementById('edit-email-new').value.length > 0)
        document.getElementById('user-personal-email').innerText = document.getElementById('edit-email-new').value;

}


// to clear all registration page fields after successfully registering or moving to different page
export function clearAllRegisterFields() {
    document.getElementById('username-register').value = '';
    document.getElementById('password-register').value = '';
    document.getElementById('confirm-register').value = '';
    document.getElementById('email-register').value = '';
    document.getElementById('name-register').value = '';
}


// to clear all login page fields after successfully registering or moving to different page
export function clearAllLoginFields () {
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    document.getElementById('confirm-password').value = '';
}


// remove all filled details on edit pop up box
export function removeDetailsOfEditProfile() {
    document.getElementById('edit-name-new').value = '';
    document.getElementById('edit-email-new').value = '';
    document.getElementById('edit-password-new').value = '';
}


// to show error alert when any error occurs
export function showErrorAlert(errorMessage) {
    document.getElementById('error-popup-message').innerText = errorMessage;
    document.getElementById('error-popup-box').style.display = 'block';
}


// to show error alert when any error occurs
export function showCautionAlert(errorMessage) {
    document.getElementById('caution-popup-message').innerText = errorMessage;
    document.getElementById('caution-popup-box').style.display = 'block';
}


// to show success alert when any operation is successful
export function showSuccessAlert(successMessage) {
    document.getElementById('success-popup-message').innerText = successMessage;
    document.getElementById('success-popup-box').style.display = 'block';
}


// creating message for new user with no feeds to show in user feed
export function loadNewUserMessage(newUserBox) {    
    const newMessage = document.createElement('div');
    newMessage.innerText = 'Welcome to Quickpic! ';
    newMessage.innerText += 'It seems that you have not followed any users who have posted any images yet.';
    newMessage.innerText += 'You can search any user with their username using our special search box on top right corner and follow them.';
    newUserBox.appendChild(newMessage);
}


// adding event to like button using this function to show all the likes for a post
export function addEventShowLikes(event, page) {

    let postID = event.target.id.split('-')[4];    
    let showLikesPopUp = document.getElementById(`${page}-likes-popup-${postID}`);

    if (showLikesPopUp.style.visibility === 'visible') {
        showLikesPopUp.style.visibility = 'hidden';   

    } else {
        showLikesPopUp.style.visibility = 'visible';  
    }
}
            

// adding event to comment button using this function to show all the comments for a post
export function addEventShowComments(event, page) {

    let postID;
    if (event.target.className === 'comment-btn') {
        postID = event.target.id.split('-')[3];
    } else if (event.target.className === 'home-comments-count-btn' || event.target.className === 'user-comments-count-btn') {
        postID = event.target.id.split('-')[4];
    } 

    // get boxes for comment text input and all comments by their IDs
    let commentsInputBoxElement = document.getElementById(`${page}-comment-write-box-${postID}`);
    let commentsPostCommentsElement = document.getElementById(`${page}-comments-show-box-${postID}`);
                                
    // if the boxes are visible, then hide them and vice-versa
    if (commentsInputBoxElement.style.display === 'block' && commentsPostCommentsElement.style.display === 'block') {
        commentsInputBoxElement.style.display = 'none';
        commentsPostCommentsElement.style.display = 'none';

    } else {
        commentsInputBoxElement.style.display = 'block';
        commentsPostCommentsElement.style.display = 'block';
    }          
}
