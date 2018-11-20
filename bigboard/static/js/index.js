$(function(){
    pathname = window.location.pathname.substring(1);
    switch(pathname) {
        case "":
            $('#home-tab').addClass('active')
            break;
        case "gallery":
            $('#gallery-tab').addClass('active')
            break;
        case "broadcast":
            $('#broadcast-tab').addClass('active')
            break;
        case "formation":
            $('#formation-tab').addClass('active')
            break;
        default:
            break;
    }
});