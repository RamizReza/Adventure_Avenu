function changeText(){
htxt. innerText= Date();
console.log('button Cliked');

}
z= multi(x,y);

console.log(z);

function multi(x,y){
    let c =x*y;
    return c;

}

greeting()

function greeting(){
    const time = new Date().getHours();

    if(time<9){
        console.log('good morning')
    }

    else{
        console.log('have a good day')
    }
}