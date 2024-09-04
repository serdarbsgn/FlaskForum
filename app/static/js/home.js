// Get a reference to the canvas element
const canvas = document.getElementById('homeCanvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const ch10 = canvas.height/10;
const ch20 = ch10/2;
const ch5 = ch10*2;
const cw10 = canvas.width/10;
const cw20 = cw10/2;
const max_magnitude = 3;
const rectangles = (() => {
    if (user) {return [
{"x":0,"y":-ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/home","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-2*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/forums","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-3*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/market","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-4*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/games","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-5*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/gyrowheel","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-6*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/logout","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-7*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/cart","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-8*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/orders","shrink":true,"magnitude":1,"iframe":null},
{"x":-canvas.width,"y":-canvas.height,"w":canvas.width,"h":2*canvas.height,"vx":0,"vy":0,"ec":0,"static":true,"href":"Left Wall","shrink":true,"magnitude":1,"iframe":null},
{"x":canvas.width,"y":-canvas.height,"w":canvas.width,"h":2*canvas.height,"vx":0,"vy":0,"ec":0,"static":true,"href":"Right Wall","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":canvas.height,"w":canvas.width,"h":canvas.height,"vx":0,"vy":0,"ec":0,"static":true,"href":"Ground","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-2*canvas.height,"w":canvas.width,"h":canvas.height,"vx":0,"vy":0,"ec":0,"static":true,"href":"Roof","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":canvas.height/2,"w":canvas.width/5,"h":ch20,"vx":0,"vy":0,"ec":0,"static":true,"href":"Shelf","shrink":true,"magnitude":1,"iframe":null},
{"x":canvas.width-canvas.width/4,"y":canvas.height/5,"w":canvas.width/4,"h":ch20,"vx":0,"vy":0,"ec":0,"static":true,"href":"Shelf","shrink":true,"magnitude":1,"iframe":null},
]
}else {
return [
{"x":0,"y":-ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/home","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-2*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/forums","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-3*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/market","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-4*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/games","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-5*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/gyrowheel","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-6*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/login","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-7*ch10,"w":cw10,"h":ch10,"vx":getRandomInt(-3,3),"vy":0,"ec":getRandomInt(25,60)/100,"static":false,"href":"/register","shrink":true,"magnitude":1,"iframe":null},
{"x":-canvas.width,"y":-canvas.height,"w":canvas.width,"h":2*canvas.height,"vx":0,"vy":0,"ec":0,"static":true,"href":"Left Wall","shrink":true,"magnitude":1,"iframe":null},
{"x":canvas.width,"y":-canvas.height,"w":canvas.width,"h":2*canvas.height,"vx":0,"vy":0,"ec":0,"static":true,"href":"Right Wall","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":canvas.height,"w":canvas.width,"h":canvas.height,"vx":0,"vy":0,"ec":0,"static":true,"href":"Ground","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":-2*canvas.height,"w":canvas.width,"h":canvas.height,"vx":0,"vy":0,"ec":0,"static":true,"href":"Roof","shrink":true,"magnitude":1,"iframe":null},
{"x":0,"y":canvas.height/2,"w":canvas.width/5,"h":ch20,"vx":0,"vy":0,"ec":0,"static":true,"href":"Shelf","shrink":true,"magnitude":1,"iframe":null},
{"x":canvas.width-canvas.width/4,"y":canvas.height/5,"w":canvas.width/4,"h":ch20,"vx":0,"vy":0,"ec":0,"static":true,"href":"Shelf","shrink":true,"magnitude":1,"iframe":null},
]}
})();
let staticCount = 0;
for(let i=0;i<rectangles.length;i++){
if(rectangles[i].static){
    staticCount +=1;
}
}
let lastFrameTime = 0;
const frameDelay = 1000 / 165;
const mouseCoordinates = [0,0];
const heldRectLastCoords = [0,0];
const heldRectSpeed = [0,0];
const heldRectOffset=[0,0];
let heldRectIndex = -1;
let gamepadHeldRectIndex = -1;
let gamepadConnected = 0;
let gamepadArrowDelay = 15;
let highlightRectPad = 0;
const g = 0.4;
let clickedRectIndex = -1;


function getSpaces(){
let width = canvas.width;
rectangles.forEach((rect,index) => {
    if(!rect.static){
        ctx.font = cw20+'px Arial';
        width -= ctx.measureText(rect.href).width;}
})
width = width / (rectangles.length+1-staticCount);
return width;
}

function initializeRectangles(){
let spaces = getSpaces();
let cumulativeX = spaces;
rectangles.forEach((rect,index) => {
    if(!rect.static){
ctx.font = cw20+'px Arial';
rect.x = cumulativeX;
rect.w = ctx.measureText(rect.href).width;
cumulativeX +=rect.w+spaces;
}})

}
initializeRectangles();

function homeLoop(){
render();
requestAnimationFrame(homeLoop);
}

function render() {
const currentTime = performance.now();
const deltaTime = currentTime - lastFrameTime;
if (deltaTime > frameDelay) {
    lastFrameTime = currentTime;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // ctx.fillStyle = 'green';
    // ctx.fillRect(0,0,canvas.width,canvas.height);
    if (gamepadConnected>0 ){
        if(gamepadArrowDelay > 0){gamepadArrowDelay--;}
        updateGamepadStatus()
        ctx.fillStyle = `hsl(${Math.floor(180)}, 0%, 50%)`;
        ctx.fillRect(rectangles[highlightRectPad].x-5, rectangles[highlightRectPad].y-5, rectangles[highlightRectPad].w+10, rectangles[highlightRectPad].h+10);
    }
    else{gamepadHeldRectIndex = -1;}
    calculate_physics(rectangles);
    for(let i = rectangles.length-1;i>-1;i--){
        let rect = rectangles[i];
        if(!rect.shrink&&rect.iframe&&rect.magnitude>max_magnitude){
            ctx.fillStyle = `hsl(${i*30}, 100%, 50%)`;
            ctx.fillRect(rect.x+rect.w-cw20, rect.y-ch20/2, cw20, ch20/2);
            rect.iframe.style.left = `${rect.x}px`;
            rect.iframe.style.top = `${rect.y}px`;
            rect.iframe.style.width = `${rect.w}px`;
            rect.iframe.style.height = `${rect.h}px`;
        }
        else{
            ctx.fillStyle = `hsl(${i*30}, 100%, 50%)`;
            ctx.fillRect(rect.x, rect.y, rect.w, rect.h);
            ctx.font = cw20+'px Arial';
            ctx.fillStyle = 'black';
            if(!rect.static){
            ctx.fillText(rect.href,rect.x,rect.y+cw20*4/5);}
        }
    }
}
}

homeLoop();

function calculate_physics(rectangles) {
for (let index = 0; index < rectangles.length; index++) {
    let rect = rectangles[index];
    let colX = false;
    for (let i = rectangles.length-1; i >= index; i--) {
        if(rect.static){
            continue;//static objects don't need to be applied gravity or checked for collision because dynamic objects will calculate colliding with them.
        }
        if (index == i){
            if (rectangles[i].shrink){
                if(rectangles[i].magnitude > 1){
                    rectangles[i].magnitude -= 0.05;
                    changePageSize(i,rectangles[i].magnitude)}
            }else if (!rectangles[i].shrink){
                if(rectangles[i].magnitude < max_magnitude){
                    rectangles[i].magnitude += 0.05;
                    changePageSize(i,rectangles[i].magnitude)}
            }
            if (heldRectIndex === i) {
                heldRectLastCoords[0] = rectangles[heldRectIndex].x;
                heldRectLastCoords[1] = rectangles[heldRectIndex].y;
                // This one is controlled by user right now, no calculations on regular physics.
                continue;
            }
            if (gamepadHeldRectIndex === i) {
                // This one is controlled by user right now, no calculations on regular physics.
                continue;
            }
            if (Math.abs(rect.vx) < 0.1) {
                rect.vx = 0;
            }
            rect.x += rect.vx;
            rect.y += rect.vy;
            if(!colX){
            rect.vy += g;}
            if (rect.x < -500 || rect.x > canvas.width + 500 || rect.y > canvas.height + 500){
                rect.x = cw10;
                rect.y = -ch10;
            }
        }else{
            if (rect.x + rect.w >= rectangles[i].x &&
                rect.x <= rectangles[i].x + rectangles[i].w &&
                rect.y + rect.h >= rectangles[i].y &&
                rect.y <= rectangles[i].y + rectangles[i].h) {
                let overlapX = Math.min(rect.x+rect.w,rectangles[i].x+rectangles[i].w)-Math.max(rect.x,rectangles[i].x);
                let overlapY = Math.min(rect.y+rect.h,rectangles[i].y+rectangles[i].h)-Math.max(rect.y,rectangles[i].y);                           
                if (overlapX < overlapY) {
                    if(rectangles[i].static){
                        rect.vx = -rect.vx;
                        if (rect.x < rectangles[i].x) {
                            rect.x -= overlapX+0.1;
                        } else {
                            rect.x += overlapX+0.1;
                        }
                    }else{
                        let velocitySumX = Math.abs(rect.vx) + Math.abs(rectangles[i].vx);
                        
                        let tempRectVx = rect.vx;
                        let tempRectIVx = rectangles[i].vx;
                        rect.vx = (velocitySumX * tempRectIVx) / (Math.abs(tempRectVx) + Math.abs(tempRectIVx)) - rect.ec;
                        if (isNaN(rect.vx)) {
                            rect.vx = 0;
                        }
                        rectangles[i].vx = (velocitySumX * tempRectVx) / (Math.abs(tempRectVx) + Math.abs(tempRectIVx)) - rectangles[i].ec;
                        if (isNaN(rectangles[i].vx)) {
                            rectangles[i].vx = 0;
                        }
                        if (rect.x < rectangles[i].x) {
                            rect.x -= overlapX / 2;
                            rectangles[i].x += overlapX / 2+0.1;
                        } else {
                            rect.x += overlapX / 2;
                            rectangles[i].x -= overlapX / 2+0.1;
                        }
                    }
                } else {
                    if(rectangles[i].static){
                        rect.vy = -rect.vy * rect.ec;
                        if (Math.abs(rect.vy) < rect.ec * 3) {
                        rect.vy = 0;
                        }
                        if (rect.y < rectangles[i].y) {
                            rect.y -= overlapY+0.1;
                            colX=true;
                        }else {
                            rect.y += overlapY+0.1;
                        }
                    }else{
                        let velocitySumY = Math.abs(rect.vy) + Math.abs(rectangles[i].vy);
                        let tempRectVy = rect.vy;
                        let tempRectIVy = rectangles[i].vy;
                        rect.vy = (velocitySumY * tempRectIVy) / (Math.abs(tempRectVy) + Math.abs(tempRectIVy));
                        if (isNaN(rect.vy)) {
                            rect.vy = 0;
                        }
                        rectangles[i].vy = (velocitySumY * tempRectVy) / (Math.abs(tempRectVy) + Math.abs(tempRectIVy));
                        if (isNaN(rectangles[i].vy)) {
                            rectangles[i].vy = 0;
                        }
                        if (rect.y < rectangles[i].y) {
                            colX=true;
                            rect.y -= overlapY / 2;
                            rectangles[i].y += overlapY / 2;
                        } else {
                            rect.y += overlapY / 2;
                            rectangles[i].y -= overlapY / 2;
                        }
                    }
                    if (rect.vx > 0) {
                            rect.vx -= rect.ec / 8;
                        }
                    else if (rect.vx < 0) {
                        rect.vx += rect.ec / 8;
                    }
                }
            }
        }                              
    }
}
}

function applyVelocityChanges(rect, other, axis) {
let velocitySum = Math.abs(rect[axis]) + Math.abs(other[axis]);
let tempRectV = rect[axis];
let tempOtherV = other[axis];

rect[axis] = (velocitySum * tempOtherV) / (Math.abs(tempRectV) + Math.abs(tempOtherV)) - rect.ec;
if (isNaN(rect[axis])) {
rect[axis] = 0;
}
other[axis] = (velocitySum * tempRectV) / (Math.abs(tempRectV) + Math.abs(tempOtherV)) - other.ec;
if (isNaN(other[axis])) {
other[axis] = 0;
}
}


function getRandomInt(min, max) {
return Math.floor(Math.random() * (max - min + 1)) + min;
}

function changePageSize(index,magnitude){
ctx.font = cw20+'px Arial';
let abs_width_x = ctx.measureText(rectangles[index].href).width*magnitude;
let abs_width_y = ch10*magnitude;
if(canvas.width < abs_width_x){
    magnitude = rectangles[index].magnitude - 0.05;
}else if(canvas.height < abs_width_y){
    magnitude = rectangles[index].magnitude - 0.05;
}else if(magnitude < 1){
    magnitude = 0.99;
    rectangles[index].w = ctx.measureText(rectangles[index].href).width*magnitude;
    rectangles[index].h = ch10*magnitude;
}else{
    rectangles[index].magnitude = magnitude;
    rectangles[index].w = ctx.measureText(rectangles[index].href).width*magnitude;
    rectangles[index].h = ch10*magnitude;}
    
let r = rectangles[index];
if(magnitude > max_magnitude){
    if(!r.iframe){
    r.iframe = document.createElement('iframe');
    r.iframe.src = r.href+"?hide_header=1";
    r.iframe.style.width = '100%';
    r.iframe.style.height = '100%';
    r.iframe.style.left = `${r.x}px`;
    r.iframe.style.top = `${r.y}px`;
    r.iframe.style.width = `${r.w}px`;
    r.iframe.style.height = `${r.h}px`;
    r.iframe.style.position = 'absolute';
    r.iframe.setAttribute('frameborder', '0');
    document.body.appendChild(r.iframe);}
    else{
        r.iframe.style.display = 'block';
        r.iframe.style.left = `${r.x}px`;
        r.iframe.style.top = `${r.y}px`;
        r.iframe.style.width = `${r.w}px`;
        r.iframe.style.height = `${r.h}px`;
        r.iframe.style.position = 'absolute'
    }
    //iframe works better imo.
    // const windowFeatures = `width=${rectangles[index].w},height=${rectangles[index].h},left=${rectangles[index].x},top=${rectangles[index].y}`;
    // window.open(rectangles[index].href, '_blank', windowFeatures);
}
if(magnitude<max_magnitude)
{
    if(r.iframe){
        r.iframe.style.display = 'none';
        document.body.removeChild(r.iframe);
        r.iframe = null;
    }
}

}
function resetPage(index){
ctx.font = cw20+'px Arial';
rectangles[index].w = ctx.measureText(rectangles[index].href).width;
rectangles[index].h = ch10;
}

function mouseClicked(e) {

if (e.button === 0) {
    for(let i = 0; i < rectangles.length; i++) {
        if(rectangles[i].static){
            continue;
        }
        if (
            mouseCoordinates[0] > rectangles[i].x &&
            mouseCoordinates[0] < rectangles[i].x + rectangles[i].w &&
            mouseCoordinates[1] > rectangles[i].y &&
            mouseCoordinates[1] < rectangles[i].y + rectangles[i].h
        ) {
            if (rectangles[i].shrink){
                rectangles[i].shrink = false;
                // rectangles[i].static = true;
                rectangles[i].vx = 0;
                rectangles[i].vy = 0;
            }
            else{
                rectangles[i].shrink = true;
                // rectangles[i].static = false;
            }
            

            break;
        }
        else if(
            mouseCoordinates[0] > rectangles[i].x+rectangles[i].w -cw20 &&
            mouseCoordinates[0] < rectangles[i].x+rectangles[i].w  &&
            mouseCoordinates[1] > rectangles[i].y-ch20/2 &&
            mouseCoordinates[1] < rectangles[i].y && !rectangles[i].shrink
        ){

            rectangles[i].shrink = true;
            // rectangles[i].static = false;
        }
    }
}

if (e.button === 2) {
    for(let i = 0; i < rectangles.length; i++) {
        if(rectangles[i].static){
            continue;
        }
        if(rectangles[i].shrink){
        if (
            mouseCoordinates[0] > rectangles[i].x &&
            mouseCoordinates[0] < rectangles[i].x + rectangles[i].w &&
            mouseCoordinates[1] > rectangles[i].y &&
            mouseCoordinates[1] < rectangles[i].y + rectangles[i].h
        ) {
            heldRectOffset[0] = rectangles[i].x - mouseCoordinates[0];
            heldRectOffset[1] = rectangles[i].y - mouseCoordinates[1];
            heldRectIndex = i;
            break;
            }
        }
        else{
            if(
            mouseCoordinates[0] > rectangles[i].x+rectangles[i].w -cw20 &&
            mouseCoordinates[0] < rectangles[i].x+rectangles[i].w  &&
            mouseCoordinates[1] > rectangles[i].y-ch20/2 &&
            mouseCoordinates[1] < rectangles[i].y
            ){
            heldRectOffset[0] = rectangles[i].x - mouseCoordinates[0];
            heldRectOffset[1] = rectangles[i].y - mouseCoordinates[1];
            heldRectIndex = i;
            break;}
        }
    }
}
}

function mouseReleased(e) {
if (e.button === 0) {

}

if (e.button === 2) {
    if (heldRectIndex != -1){
    heldRectOffset[0] = 0;
    heldRectOffset[1] = 0;
    rectangles[heldRectIndex].vx = heldRectSpeed[0];
    rectangles[heldRectIndex].vy = heldRectSpeed[1];
    heldRectIndex= -1;
    }
}
}
function mouseMoved(e) {
mouseCoordinates[0] = e.clientX - canvas.offsetLeft;
mouseCoordinates[1] = e.clientY - canvas.offsetTop;
if (heldRectIndex != -1){
rectangles[heldRectIndex].x = mouseCoordinates[0] + heldRectOffset[0];
rectangles[heldRectIndex].y = mouseCoordinates[1] + heldRectOffset[1];
rectangles[heldRectIndex].vx = 0;
rectangles[heldRectIndex].vy = 0;

const currentTime = performance.now()
let deltaX = rectangles[heldRectIndex].x - heldRectLastCoords[0];
let deltaY = rectangles[heldRectIndex].y - heldRectLastCoords[1];
heldRectSpeed[0] = deltaX / (currentTime-lastFrameTime)
heldRectSpeed[1] = deltaY / (currentTime-lastFrameTime)
}
}

function mouseWheel(e){
direction = Math.sign(e.deltaY)
if(direction<0){
    for(let i = 0; i < rectangles.length; i++) {
        if(rectangles[i].static){
            continue;
        }
        if (
            mouseCoordinates[0] > rectangles[i].x &&
            mouseCoordinates[0] < rectangles[i].x + rectangles[i].w &&
            mouseCoordinates[1] > rectangles[i].y &&
            mouseCoordinates[1] < rectangles[i].y + rectangles[i].h && rectangles[i].magnitude<3
        ) {
            rectangles[i].magnitude += 0.1;
            let magnitude = rectangles[i].magnitude+ 0.05;
            if(rectangles[i].magnitude>max_magnitude){
                
                rectangles[i].shrink = false;
            }
            changePageSize(i,magnitude)
            break;
        }
        else if(
            mouseCoordinates[0] > rectangles[i].x+rectangles[i].w -cw20 &&
            mouseCoordinates[0] < rectangles[i].x+rectangles[i].w  &&
            mouseCoordinates[1] > rectangles[i].y-ch20/2 &&
            mouseCoordinates[1] < rectangles[i].y && !rectangles[i].shrink
        ){
            rectangles[i].magnitude += 0.1;
            let magnitude = rectangles[i].magnitude + 0.05;
            if(rectangles[i].magnitude>max_magnitude){
                rectangles[i].shrink = false;
            }
            changePageSize(i,magnitude)
            break;
        }
    }
}else if(direction>0){
    for(let i = 0; i < rectangles.length; i++) {

    if (
        mouseCoordinates[0] > rectangles[i].x &&
        mouseCoordinates[0] < rectangles[i].x + rectangles[i].w &&
        mouseCoordinates[1] > rectangles[i].y &&
        mouseCoordinates[1] < rectangles[i].y + rectangles[i].h && rectangles[i].magnitude<3
    ) {
        rectangles[i].magnitude -= 0.1;
        let magnitude = rectangles[i].magnitude-0.05;
        if(rectangles[i].magnitude<max_magnitude){
            rectangles[i].shrink = true;
        }
        changePageSize(i,magnitude)
        break;
    }
    else if(
        mouseCoordinates[0] > rectangles[i].x+rectangles[i].w -cw20 &&
        mouseCoordinates[0] < rectangles[i].x+rectangles[i].w  &&
        mouseCoordinates[1] > rectangles[i].y-ch20/2 &&
        mouseCoordinates[1] < rectangles[i].y && !rectangles[i].shrink
    ){
        rectangles[i].magnitude -= 0.1;
        let magnitude = rectangles[i].magnitude-0.05;
        if(rectangles[i].magnitude < max_magnitude){
            rectangles[i].shrink = true;
        }
        changePageSize(i,magnitude)
        break;
    }
    }
}
}
canvas.addEventListener('wheel',mouseWheel);
canvas.addEventListener('mousedown', mouseClicked);
canvas.addEventListener('mouseup', mouseReleased);
canvas.addEventListener('mousemove', mouseMoved);


window.addEventListener("gamepadconnected", (event) => {
gamepadConnected += 1;
});

window.addEventListener("gamepaddisconnected", (event) => {
gamepadConnected -= 1;
});

function updateGamepadStatus() {
const currentGamepads = navigator.getGamepads();
let gp = null;
for (let j = 0; j < currentGamepads.length; j++){
    if(currentGamepads[j] !== null){gp=currentGamepads[j]}
}
let buttonPressed = false;
if (gp) {
    for (let j = 0; j < gp.buttons.length; j++) {
        if (gp.buttons[j].pressed) {
            if (j == 14) { // Left arrow on Xbox controller
                if (gamepadArrowDelay <= 0) {
                    highlightRectPad = Math.max(-1, highlightRectPad - 1);
                    if (highlightRectPad == -1) {
                        highlightRectPad = rectangles.length - 1 -staticCount;
                    }
                    gamepadArrowDelay = 15;
                }
            } else if (j == 15) { // Right arrow on Xbox controller
                if (gamepadArrowDelay <= 0) {
                    highlightRectPad = Math.min(rectangles.length-staticCount, highlightRectPad + 1);
                    if (highlightRectPad == rectangles.length-staticCount) {
                        highlightRectPad = 0;
                    }
                    gamepadArrowDelay = 15;
                }
            } else if(j == 0){
                if (gamepadArrowDelay <= 0) {
                    if (rectangles[highlightRectPad].shrink){
                        rectangles[highlightRectPad].shrink = false;
                        // rectangles[highlightRectPad].static = true;
                        rectangles[highlightRectPad].vx = 0;
                        rectangles[highlightRectPad].vy = 0;
                        }
                    else{
                        rectangles[highlightRectPad].shrink = true;
                        // rectangles[highlightRectPad].static = false;
                    }
                    gamepadArrowDelay = 15;
                }
            }else { // Other buttons for holding object in place
                gamepadHeldRectIndex = highlightRectPad;
                rectangles[gamepadHeldRectIndex].vx = 0;
                rectangles[gamepadHeldRectIndex].vy = 0;
                buttonPressed = true;
            }
        }
    }

    if (!buttonPressed) {
        gamepadHeldRectIndex = -1;
    }  
}
if(gp.axes.length > 0){
    for (let k = 0; k < gp.axes.length; k++) {
            if (Math.abs(gp.axes[k]) > 0.1) { // Simple dead zone check
                if (gamepadHeldRectIndex != -1) {
                    if (k == 1) { // Left analog's y axis
                        rectangles[gamepadHeldRectIndex].y += gp.axes[k] * 5;
                        rectangles[gamepadHeldRectIndex].vy = gp.axes[k] * 5;
                    }
                    if (k == 0) { // Left analog's x axis
                        rectangles[gamepadHeldRectIndex].x += gp.axes[k] * 5;
                        rectangles[gamepadHeldRectIndex].vx = gp.axes[k] * 5;
                    }
                }
            }
        }
    }
}

function listenIframeMessage(message){
if(message.data.response=='Logged In'){
    window.location.reload()
}
else if(message.data.response=='Logged Out'){
    window.location.reload()
}
}
window.addEventListener('message',listenIframeMessage)
