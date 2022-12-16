const handleExpandables = (y) => {
    let x = document.getElementById('nav-btns');
    if (x !== y && x.className !== 'nav-btn-container') {
        console.log('here');
        x.className = "nav-btn-container";
    }
    x = document.getElementById('nav-user-menu');
    if (x !== y && x.style.display === 'flex') {
        x.style.display = 'flex';
        console.log('here2');
    }
    x = document.getElementById('search-icon');
    if (x !== y && x.style.display !== 'none') {
        searchCloseClick();
        console.log('here3');
    }

}

const navMenuClick = () => {
    let x = document.getElementById('nav-btns');
    // handleExpandables(x);
    if (x.className === "nav-btn-container") {
        x.className = "nav-dropdown";
    }
    else {
        x.className = "nav-btn-container";
    }
}

var navBtnDisplay;

const setNavBtnDisplayToNone = () => {
    navBtnDisplay = document.getElementById('nav-btns').style.display;
    document.getElementById('nav-btns').style.display = 'none';
}
const resetNavBtnDisplay = () => {
    document.getElementById('nav-btns').style.display = navBtnDisplay;
}

const searchIconClick = () => {
    let x = document.getElementById('search-icon');
    // handleExpandables(x);
    x.style.display = 'none';
    setNavBtnDisplayToNone();
    document.getElementById('nav-search-form').style.display = 'flex';
    if (window.innerWidth <= 900 && window.innerWidth > 440) {
        document.getElementsByClassName('logo-container')[0].style.display = 'none';
    }
    document.getElementById('search-bar-input').focus();
}

const searchCloseClick = () => {
    document.getElementById('search-icon').style.display = 'block';
    resetNavBtnDisplay();
    document.getElementById('nav-search-form').style.display = 'none';
    if (window.innerWidth <= 1080 && window.innerWidth > 580) {
        document.getElementsByClassName('logo-container')[0].style.removeProperty('display');
    }
    document.getElementById('search-bar-input').blur();
}

const userIconClick = () => {
    x = document.getElementById('nav-user-menu')
    fetch('/users/new_notifications', {
        method: 'GET',
    }).then((response) => {
        if (response.status === 200) {
            return response.json();
        }
    }).then((data) => {
        if (data.notification_count > 0) {
            document.getElementById('notification-user-menu').innerHTML = "Notifications (" + data.notification_count + ")";
        }
    });

    if (x.style.display === 'flex') {
        x.style.display = 'none';
    }
    else {
        x.style.display = 'flex';
    }
}

const sidebarButtonClick = () => {
    let x = document.getElementById('sidebar-button')
    let y = document.getElementsByClassName('profile-sidebar')[0];
    if (x.className === 'fa-solid fa-arrow-right fa-2xl') {
        x.className = 'fa-solid fa-arrow-left fa-2xl';
        y.style.display = 'flex';
        document.getElementsByClassName('profile-sidebar-container')[0].focus();
    }
    else {
        x.className = 'fa-solid fa-arrow-right fa-2xl'
        document.getElementsByClassName('profile-sidebar-container')[0].blur();
        y.style.removeProperty('display');
    }
}

const popUpButton = (id) => {
    let x = document.getElementById(id);
    if (x.style.display === "flex") {
        x.style.removeProperty('display');
    }
    else {
        x.style.display = "flex";

    }
}

var starClassnames = [];

const storeStarClass = () => {
    for (let i = 1; i <= 5; i++)
        starClassnames.push(document.getElementById('star' + i).className);
}

const restoreStarClass = () => {
    for (let i = 1; i <= 5; i++)
        document.getElementById('star' + i).className = starClassnames[i - 1];

    starClassnames = [];
}

const starClick = (id) => {
    id = parseInt(id[4]);
    document.getElementById('star-' + id).checked = true;
    for (let i = 1; i <= id; i++) {
        document.getElementById('star' + i).className = 'fa-solid fa-star fa-2xl';
    }
    starClassnames = [];
}

const starMouseOver = (id) => {
    id = parseInt(id[4]);
    if (starClassnames.length === 0) {
        storeStarClass();
    }
    for (let i = 1; i <= id; i++) {
        document.getElementById('star' + i).className = 'fa-solid fa-star fa-2xl';
    }
    for (let i = id + 1; i <= 5; i++) {
        document.getElementById('star' + i).className = 'fa-regular fa-star fa-2xl';
    }
}

const starMouseOut = () => {
    if (starClassnames.length === 0)
        return
    restoreStarClass();
}

const changeUrl = (url) => {
    location.href = url;
}
// `{{ url_for('user.follow', username=user.username) }}`

const react = (like, post_id) => {
    fetch('/post/react', {
        method: 'POST',
        body: JSON.stringify({
            like: like,
            post_id: post_id,
        })
    }).then((response) => {
        if (response.status === 200) {
            return response.json();
        }
    }).then((data) => {
        x = document.getElementById('like' + post_id);
        y = document.getElementById('dislike' + post_id);
        if (data.reaction) {
            x.classList.add('reacted');
            y.classList.remove('reacted');
        }
        else if (data.reaction === null) {
            x.classList.remove('reacted');
            y.classList.remove('reacted');
        }
        else {
            x.classList.remove('reacted');
            y.classList.add('reacted');
        }
    })
}

const follow = (username, element) => {

    if (element.innerHTML === 'Follow') {
        fetch('/users/follow/' + username, {
            method: 'GET'
        }).then((response) => {
            if (response.status === 200) {
                element.innerHTML = 'Unfollow';
            }
        })
    }
    else {
        fetch('/users/unfollow/' + username, {
            method: 'GET'
        }).then((response) => {
            if (response.status === 200) {
                element.innerHTML = 'Follow';
            }
        })
    }
}

$(document).ready(function () {
    setTimeout(function () {
        $('.flash-message').fadeOut('slow');
    }, 1500)
});