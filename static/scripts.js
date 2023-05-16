
// You are not supposed to be here!! You sneaky snake! D:
// Oh well.. Since you are so sneaky you don't have to decipher the message..

var message = "Woah! You are actually checking the console! Are you a hacker or something?? Try adding this to the console and see what happens: console_heck";
function rot13(str) {
    var input     = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    var output    = 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm';
    var index     = x => input.indexOf(x);
    var translate = x => index(x) > -1 ? output[index(x)] : x;
    return str.split('').map(translate).join('');
}

console.log(rot13(message));