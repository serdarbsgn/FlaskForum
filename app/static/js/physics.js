//make sure to have a <canvas id="gameCanvas" width="800" height="800"></canvas> canvas object like this before importing it.
const canvas = document.getElementById('gameCanvas');
canvas.width = parseInt(window.innerWidth/10)*9;
canvas.height = parseInt(window.innerHeight/10)*8;
const ctx = canvas.getContext('2d');
let mouseCoordinates = [0,0]
let heldRectLastCoords = [0,0]
let heldRectSpeed = [0,0]
let heldRectOffset=[0,0]
let gamepadConnected = 0;
let gamepadArrowDelay = 10;
let highlightRectPad = 0;
let cubes = createRandomArray(10)
let heldRectIndex = -1;
let gamepadHeldRectIndex = -1;
let g = 0.5;
let lastFrameTime = 0;
const frameDelay = 1000 / 165;
// Main game loop
function gameLoop() {
        render();
        requestAnimationFrame(gameLoop);
    }

// Function to render the game state
function render() {
    const currentTime = performance.now();
    const deltaTime = currentTime - lastFrameTime;

    if (deltaTime > frameDelay) {
        lastFrameTime = currentTime;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'darkgray';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'lightgray';
        ctx.fillRect(20, 20, canvas.width-40, canvas.height-40);

        calculate_physics(cubes)
        if (gamepadConnected>0 ){
            updateGamepadStatus()
            ctx.fillStyle = `hsl(${Math.floor(180)}, 0%, 50%)`;
            ctx.fillRect(cubes[highlightRectPad][0]-5, cubes[highlightRectPad][1]-5, cubes[highlightRectPad][5]+10, cubes[highlightRectPad][6]+10);
        }
        else{gamepadHeldRectIndex = -1;}
        for(let i=0; i< cubes.length;i++){
            ctx.fillStyle = `hsl(${Math.floor(i * 30)}, 100%, 50%)`;
            ctx.fillRect(cubes[i][0], cubes[i][1], cubes[i][5], cubes[i][6]);
            }

        }

    }
function calculate_physics(cubes){
    for(let i=0;i<cubes.length;i++){
        calculate_collisions(i)
        if(heldRectIndex == i){
            heldRectLastCoords[0] = cubes[heldRectIndex][0];
            heldRectLastCoords[1] = cubes[heldRectIndex][1];
            //This one is controlled by user right now, no calculations on regular physics.
            continue;
        }
        if(gamepadHeldRectIndex == i){
            //This one is controlled by user right now, no calculations on regular physics.
            continue;
        }
        let pos = cubes[i]
        if(Math.abs(pos[2])<0.1){
            pos[2] = 0;
        }
        pos[0] = pos[0]+pos[2]
        if(pos[0] > canvas.width-pos[5]-20){
            pos[0] = canvas.width-pos[5]-20;
            pos[2] = -Math.abs(pos[2]);
        }
        if(pos[0] < 20){
            pos[0] = 20;
            pos[2] = Math.abs(pos[2]);
        }
        if(pos[3]>0)
        {
            if( pos[1] < canvas.height - pos[6] - 20){
                pos[1] = pos[1] + pos[3]
                pos[3] = pos[3]+g
            }
            else{
                pos[1] = canvas.height - pos[6] - 20
                pos[3] = -pos[3] * pos[4]
                if(Math.abs(pos[3]) < pos[4]*3) {
                    pos[3] = 0;
                    pos[1] = canvas.height - pos[6] - 20;
                }
            }
        }
        else if (pos[3] == 0 && pos[1] == canvas.height- pos[6]-20)
        {
            if (pos[2] > 0){
                pos[2] -= pos[4]/8
            }
            if (pos[2] < 0){
                pos[2] += pos[4]/8
            }
        }else{
            pos[1] = pos[1]+pos[3]
            pos[3] = pos[3] + g
            
            
        }
    }
}
function calculate_collisions(index) {
    let pos = cubes[index];
    for (let i = index + 1; i < cubes.length; i++) {
        if (pos[0] + pos[5] >= cubes[i][0] &&    
            pos[0] <= cubes[i][0] + cubes[i][5] &&    
            pos[1] + pos[6] >= cubes[i][1] &&    
            pos[1] <= cubes[i][1] + cubes[i][6]) {   
                 
            let velocitySumX = Math.abs(pos[2]) + Math.abs(cubes[i][2]);
            let velocitySumY = Math.abs(pos[3]) + Math.abs(cubes[i][3]);

            let tempPos2 = pos[2];
            let tempCubesI2 = cubes[i][2];
            let tempPos3 = pos[3];
            let tempCubesI3 = cubes[i][3];



            let overlapX = Math.ceil((pos[5] + cubes[i][5]) / 2 - Math.abs((pos[0] + pos[5] / 2) - (cubes[i][0] + cubes[i][5] / 2)));
            let overlapY = Math.ceil((pos[6] + cubes[i][6]) / 2 - Math.abs((pos[1] + pos[6] / 2) - (cubes[i][1] + cubes[i][6] / 2)));
            if (overlapX < overlapY) {

                pos[2] = (velocitySumX * tempCubesI2) / (Math.abs(tempPos2) + Math.abs(tempCubesI2));
                if (isNaN(pos[2])){
                    pos[2] = 0;
                } 
                cubes[i][2] = (velocitySumX * tempPos2) / (Math.abs(tempPos2) + Math.abs(tempCubesI2));
                if (isNaN(cubes[i][2])){
                    cubes[i][2] = 0;
                } 
                if (pos[0] < cubes[i][0]) {
                    pos[0] -= overlapX / 2;
                    cubes[i][0] += overlapX / 2;
                } else {
                    pos[0] += overlapX / 2;
                    cubes[i][0] -= overlapX / 2;
                }
            } else {
                //Sometimes, this leads to 0/0 which is NaN and causes to make rectangles disappear, so we need to check for that.
                pos[3] = (velocitySumY * tempCubesI3) / (Math.abs(tempPos3) + Math.abs(tempCubesI3));
                if (isNaN(pos[3])){
                    pos[3] = 0;
                } 
                cubes[i][3] = (velocitySumY * tempPos3) / (Math.abs(tempPos3) + Math.abs(tempCubesI3));
                if (isNaN(cubes[i][3])){
                    cubes[i][3] = 0;
                } 
                if (pos[1] < cubes[i][1]) {
                    pos[1] -= overlapY / 2;
                    cubes[i][1] += overlapY / 2;
                } else {
                    pos[1] += overlapY / 2;
                    cubes[i][1] -= overlapY / 2;
                }
            }
        }
    }
    
}
function createRandomArray(rows) {
    const result = [];

    for (let i = 0; i < rows; i++) {
        const row = [];
        row.push(getRandomInt(1, 1000)); //x 
        row.push(getRandomInt(1, 1000)); //y 
        row.push(getRandomInt(-20, 20)); //vx
        row.push(getRandomInt(-20, 20)); //vy
        row.push(getRandomInt(30,70)/100); //elasticity
        row.push(getRandomInt(25, 60)); //width
        row.push(getRandomInt(25, 60)); //height
        result.push(row);
    }
    return result;
}

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
document.addEventListener('keydown', function(event) {

if ((event.key == 'ArrowUp' || event.key.toUpperCase() == 'W'))  {
    cubes = createRandomArray(20);
}
})
function mouseClicked(e) {
    if (e.button === 0) {
        for(let i = 0; i < cubes.length;i++){
            if(mouseCoordinates[0]>cubes[i][0] && mouseCoordinates[0]<cubes[i][0]+cubes[i][5]
             && mouseCoordinates[1]>cubes[i][1]&& mouseCoordinates[1]< cubes[i][1]+cubes[i][6]){
                heldRectOffset[0] = cubes[i][0]-mouseCoordinates[0];
                heldRectOffset[1] = cubes[i][1]-mouseCoordinates[1];
                heldRectIndex = i;
                break;
            }
        }
    }
}
function mouseReleased(e) {
    if (e.button === 0) {
        if (heldRectIndex != -1){
        heldRectOffset[0] = 0;
        heldRectOffset[1] = 0;
        cubes[heldRectIndex][2] = heldRectSpeed[0];
        cubes[heldRectIndex][3] = heldRectSpeed[1];
        heldRectIndex= -1;
        }
    }
}
function mouseMoved(e) {
    mouseCoordinates[0] = e.clientX - canvas.offsetLeft;
    mouseCoordinates[1] = e.clientY - canvas.offsetTop;
    if (heldRectIndex != -1){

    cubes[heldRectIndex][0] = mouseCoordinates[0] + heldRectOffset[0];
    cubes[heldRectIndex][1] = mouseCoordinates[1] + heldRectOffset[1];
    cubes[heldRectIndex][2] = 0;
    cubes[heldRectIndex][3] = 0;

    const currentTime = performance.now()
    let deltaX = cubes[heldRectIndex][0] - heldRectLastCoords[0];
    let deltaY = cubes[heldRectIndex][1] - heldRectLastCoords[1];
    heldRectSpeed[0] = 2*deltaX / (currentTime-lastFrameTime)
    heldRectSpeed[1] = 2*deltaY / (currentTime-lastFrameTime)
    }
}

canvas.addEventListener('mousedown', mouseClicked);
canvas.addEventListener('mouseup', mouseReleased);
canvas.addEventListener('mousemove', mouseMoved);

function touchStart(e) {
        e.preventDefault();
        let touch = e.touches[0];
        mouseCoordinates[0] = touch.clientX - canvas.offsetLeft;
        mouseCoordinates[1] = touch.clientY - canvas.offsetTop;
        for (let i = 0; i < cubes.length; i++) {
            if (mouseCoordinates[0] > cubes[i][0] && mouseCoordinates[0] < cubes[i][0] + cubes[i][5] &&
            mouseCoordinates[1] > cubes[i][1] && mouseCoordinates[1] < cubes[i][1] + cubes[i][6]) {
                heldRectOffset[0] = cubes[i][0] - mouseCoordinates[0];
                heldRectOffset[1] = cubes[i][1] - mouseCoordinates[1];
                heldRectIndex = i;
                break;
            }
        }
}

function touchEnd(e) {
    e.preventDefault();
    if (heldRectIndex !== -1) {
        heldRectOffset[0] = 0;
        heldRectOffset[1] = 0;
        cubes[heldRectIndex][2] = heldRectSpeed[0];
        cubes[heldRectIndex][3] = heldRectSpeed[1];
        heldRectIndex = -1;
    }
}

function touchMove(e) {
    e.preventDefault();
    let touch = e.touches[0];
    mouseCoordinates[0] = touch.clientX - canvas.offsetLeft;
    mouseCoordinates[1] = touch.clientY - canvas.offsetTop;
    if (heldRectIndex !== -1) {
        cubes[heldRectIndex][0] = mouseCoordinates[0] + heldRectOffset[0];
        cubes[heldRectIndex][1] = mouseCoordinates[1] + heldRectOffset[1];
        cubes[heldRectIndex][2] = 0;
        cubes[heldRectIndex][3] = 0;

        const currentTime = performance.now()
        let deltaX = cubes[heldRectIndex][0] - heldRectLastCoords[0];
        let deltaY = cubes[heldRectIndex][1] - heldRectLastCoords[1];
        heldRectSpeed[0] = 4 * deltaX / (currentTime - lastFrameTime)
        heldRectSpeed[1] = 4 * deltaY / (currentTime - lastFrameTime)
    }
}

canvas.addEventListener('touchstart', touchStart);
canvas.addEventListener('touchend', touchEnd);
canvas.addEventListener('touchmove', touchMove);


window.addEventListener("gamepadconnected", (event) => {
    gamepadConnected+=1;
});

window.addEventListener("gamepaddisconnected", (event) => {
    gamepadConnected -= 1;
});


function updateGamepadStatus(){
const currentGamepads = navigator.getGamepads();
let gp = null;
for (let j = 0; j < currentGamepads.length; j++){
    if(currentGamepads[j] !== null){gp=currentGamepads[j]}
}
let buttonPressed = false;
for (let j = 0; j < gp.buttons.length; j++) {
        if (gp.buttons[j].pressed) {
            if(j == 14){//this corresponds to left arrow on Xbox controller
                if(gamepadArrowDelay <= 0){
                    highlightRectPad = Math.max(-1,highlightRectPad-1);
                    if(highlightRectPad == -1){
                        highlightRectPad = cubes.length-1;
                    }
                    gamepadArrowDelay = 10;
                }
                else{
                    gamepadArrowDelay-=1;
                }
            }
            else if(j == 15){//this corresponds to right arrow on Xbox controller
                if(gamepadArrowDelay <= 0){
                    highlightRectPad = Math.min(cubes.length,highlightRectPad+1);
                    if(highlightRectPad == cubes.length){
                        highlightRectPad = 0;
                    }
                    gamepadArrowDelay = 10;
                }
                else{
                    gamepadArrowDelay-=1;
                }
            }
            else {//other buttons correspond to holding object in place so user can move it.
            gamepadHeldRectIndex = highlightRectPad
            cubes[gamepadHeldRectIndex][2] =0;
            cubes[gamepadHeldRectIndex][3] =0;
            buttonPressed = true;
            }
        }
    }
    if(buttonPressed == false){
        gamepadHeldRectIndex = -1
    }
    if(gp.axes.length > 0){
        for (let k = 0; k < gp.axes.length; k++) {
            if (Math.abs(gp.axes[k]) > 0.1) { // Simple dead zone check
                if(gamepadHeldRectIndex!=-1){
                    if(k == 1){//if axis is 1,which is left analog's y axis
                        cubes[gamepadHeldRectIndex][1] += gp.axes[k]*5;
                        cubes[gamepadHeldRectIndex][3] = gp.axes[k]*5;
                    }
                    if(k == 0){//if axis is 0,which is left analog's x axis
                        cubes[gamepadHeldRectIndex][0] += gp.axes[k]*5;
                        cubes[gamepadHeldRectIndex][2] = gp.axes[k]*5;
                    }
                }
                
            }
        }
    }
}

gameLoop();
