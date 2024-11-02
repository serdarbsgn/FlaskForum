
//make sure to have a <canvas id="gameCanvas" width="800" height="800"></canvas> canvas object like this before importing it.
const canvas = document.getElementById('gameCanvas');
if (window.innerWidth > window.innerHeight) {
canvas.width = 690;
canvas.height = 390;
} else {
canvas.width = 390;
canvas.height = 690;
}
const ctx = canvas.getContext('2d');
const playPauseText = "Left Click on a Tile to Start"
const controlsText = "Middle Mouse Button Resets Game"
const flagText = "Right Click on a Tile to Flag it"
const flagText2 = "to Prevent Accidental Presses"
const gameOverText = "Game Over"
const youWinText = "You cleared all mines, congrats!"
let gameOver = false;
let mouseCoordinates = [0,0]
let mineField = new Array()
let cols = 28;
let rows = 16;
if(canvas.width<canvas.height){
    cols = 16;
    rows = 28;
}


for (let i = 0; i < cols; i++ ){
    mineField[i] = new Array(rows).fill(0)
}
let mineCount = 57;
let mineCountCopy = 57;
let firstClick = true;
let uncoveredSafeTiles = 0;
// Main game loop
function gameLoop() {
    if(gameOver)
    {
        if(uncoveredSafeTiles == 0){
            render();
            renderVictory();
        }else{
            uncoverAllBombs();
            render();
            renderGameOver();
        }
    }
    else
    {
        render();
        if (firstClick){
            renderControls();
        }
    }
}

// Function to render the game state
function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'darkgray';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'lightgray';
    ctx.fillRect(20, 20, canvas.width-40, canvas.height-40);
    ctx.fillStyle = 'green';
    ctx.font = 'bold 12px Arial';
    ctx.fillText(`🚩: ${mineCountCopy-mineCount}`,(canvas.width-ctx.measureText(`🚩: ${mineCountCopy-mineCount}`).width)/2,13)
    for (let i = 0; i <= cols-2; i++) {
        ctx.beginPath();
        ctx.moveTo(20+((canvas.width-40) * i / (cols-2)), ((canvas.height-40) / (rows-2))-5);
        ctx.lineTo(20+((canvas.width-40) * i / (cols-2)), canvas.height - 20);
        ctx.stroke();
    }

    for (let j = 0; j <= rows-2; j++) {
        ctx.beginPath();
        ctx.moveTo(((canvas.width-40) / (cols-2))-5, 20+((canvas.height-40)*j/(rows-2)));
        ctx.lineTo(canvas.width - 20, 20+((canvas.height-40)*j/(rows-2)));
        ctx.stroke();
    }
    for (let i = 1; i < cols - 1; i++) {
        for (let j = 1; j < rows - 1; j++) {
            if (mineField[i][j] !== 10 && mineField[i][j] !== 9) {
                if (mineField[i][j] > 50) {
                    ctx.fillStyle = 'red';
                    ctx.font = '20px Arial';
                    ctx.fillText("🚩", -8+((canvas.width-40) * i / (cols-2)), 14+((canvas.height-40)*j/(rows-2)));
                }
                if (mineField[i][j] === 0) {
                    ctx.fillStyle = 'darkgray';
                }
                if (mineField[i][j] === 1) {
                    ctx.fillStyle = 'blue';
                }
                if (mineField[i][j] === 2) {
                    ctx.fillStyle = 'rgb(0, 90, 0)';
                }
                if (mineField[i][j] === 3) {
                    ctx.fillStyle = 'red';
                }
                if (mineField[i][j] === 4) {
                    ctx.fillStyle = 'magenta';
                }
                if (mineField[i][j] === 5) {
                    ctx.fillStyle = 'yellow';
                }
                if (mineField[i][j] === 6) {
                    ctx.fillStyle = 'pink';
                }
                if (mineField[i][j] === 7) {
                    ctx.fillStyle = 'black';
                }
                if (mineField[i][j] < 50){
                ctx.font = 'bold 12px Arial';
                ctx.fillText(mineField[i][j] + "", 4+((canvas.width-40) * i / (cols-2)), 12+((canvas.height-40)*j/(rows-2)));
                }
                if (mineField[i][j] === -1){
                    ctx.font = '25px Arial';
                    ctx.fillStyle = 'red'
                    ctx.fillText("💣", -8+((canvas.width-40) * i / (cols-2)), 16+((canvas.height-40)*j/(rows-2)));
                }
            }
        }
    }
}
function renderControls(){
    ctx.fillRect(canvas.width*1/4,canvas.height*1/4,canvas.width*2/4,canvas.height*2/4);
    ctx.font = '20px Arial';
    ctx.fillStyle = 'black';
    ctx.fillText(playPauseText,(canvas.width-ctx.measureText(playPauseText).width)/2,canvas.height/2-30)
    ctx.fillText(controlsText,(canvas.width-ctx.measureText(controlsText).width)/2,canvas.height/2)
    ctx.fillText(flagText,(canvas.width-ctx.measureText(flagText).width)/2,canvas.height/2+30)
    ctx.fillText(flagText2,(canvas.width-ctx.measureText(flagText2).width)/2,canvas.height/2+50)
}
function renderGameOver(){
    ctx.font = '20px Arial';
    ctx.fillStyle = 'black';
    ctx.fillText(`${gameOverText}`,(canvas.width-ctx.measureText(`${gameOverText}`).width)/2,canvas.height/2)
}
function renderVictory() {
    ctx.font = '20px Arial';
    ctx.fillStyle = 'black';
    ctx.fillText(`${youWinText}`, (canvas.width - ctx.measureText(`${youWinText}`).width) / 2, canvas.height / 2);
}
gameLoop();

function initializeMinefield(x,y){
    for(let i = 1; i < cols-1;i++){
        for(let j = 1; j < rows-1;j++){
            if ((i == x && j == y || j==y-1||j==y+1)||(i == x-1 && j == y || j==y-1||j==y+1)||(i == x+1 && j == y || j==y-1||j==y+1)){
                mineField[i][j] = 10;
                uncoveredSafeTiles+=1;
        } else {
            if (mineCount != 0) {
                let temp = parseInt((Math.random() * 6));
                if (temp == 3) {
                    mineField[i][j] = 9;
                    mineCount--;
                } else {
                    mineField[i][j] = 10;
                    uncoveredSafeTiles+=1;
                }
            } else {
                mineField[i][j] = 10;
                uncoveredSafeTiles+=1;
            }
        }
    }   
}
for (let i = 0; i < cols; i++) {
    if (i < rows) {
        mineField[0][i] = 0;
        mineField[cols-1][i] = 0;
    }
    mineField[i][0] = 0;
    mineField[i][rows-1] = 0;
}
arrangeNumbers(x, y);
}

function arrangeNumbers(x,y){
    if (mineField[x][y] == 0 || mineField[x][y] > 50 || mineField[x][y]<9) {
    return;
}
let bombCount = -1;
if (mineField[x][y] == 9) {
    gameOver = true;
} else {
    bombCount = 0;
    uncoveredSafeTiles-=1;
    if (mineField[x - 1][y] == 9 || mineField[x - 1][y] == 108) {
        bombCount++;
    }

    if (mineField[x - 1][y - 1] == 9 || mineField[x - 1][y - 1] == 108) {
        bombCount++;
    }

    if (mineField[x][y - 1] == 9 || mineField[x][y - 1] == 108) {
        bombCount++;
    }

    if (mineField[x][y + 1] == 9 || mineField[x][y + 1] == 108) {
        bombCount++;
    }

    if (mineField[x - 1][y + 1] == 9 || mineField[x - 1][y + 1] == 108) {
        bombCount++;
    }

    if (mineField[x + 1][y] == 9 || mineField[x + 1][y] == 108) {
        bombCount++;
    }

    if (mineField[x + 1][y - 1] == 9 || mineField[x + 1][y - 1] == 108) {
        bombCount++;
    }

    if (mineField[x + 1][y + 1] == 9 || mineField[x + 1][y + 1] == 108) {
        bombCount++;
    }
}
if(uncoveredSafeTiles==0){
    gameOver=true;
}
if (bombCount == 0) {
    mineField[x][y] = 0;
    arrangeNumbers(x - 1, y);
    arrangeNumbers(x - 1, y - 1);
    arrangeNumbers(x, y - 1);
    arrangeNumbers(x - 1, y + 1);
    arrangeNumbers(x, y + 1);
    arrangeNumbers(x + 1, y);
    arrangeNumbers(x + 1, y - 1);
    arrangeNumbers(x + 1, y + 1);

} else{
    mineField[x][y] = bombCount;}
}

function flagSquare(x,y) {
    if (mineField[x][y]<9){return}
    if (mineField[x][y] < 50) {
        if (mineCountCopy > 0){
            mineField[x][y] += 99;
            mineCountCopy--;
        }
    } else {
        mineField[x][y] -= 99;
        mineCountCopy++;
    }
}
function uncoverAllBombs(){
    for (let i = 1; i < cols - 1; i++) {
        for (let j = 1; j < rows - 1; j++) {
            if (mineField[i][j] == 9){
                mineField[i][j] = -1;
            }
        }
    }
}
function mouseClicked(e) {
    normalisedCoordinates = [Math.ceil((mouseCoordinates[0]-20)/25),Math.ceil((mouseCoordinates[1]-20)/25)]
    if(gameOver){
        gameOver = false
        firstClick = true
        mineCount = 57;
        mineCountCopy = 57;
        uncoveredSafeTiles = 0;
    }
    if (e.button === 0) {
        if ( normalisedCoordinates[0] === 0 || normalisedCoordinates[0] === (cols-1) || normalisedCoordinates[1] === 0 || normalisedCoordinates[1] === (rows-1))
        {
        }
        else{
            if(firstClick){
                initializeMinefield(normalisedCoordinates[0],normalisedCoordinates[1])
                firstClick = false;
            }
            else{
                arrangeNumbers(normalisedCoordinates[0],normalisedCoordinates[1])
            }
        }
    }
    if (e.button === 1) {
        mineCount = 75;
        mineCountCopy = 75;
        initializeMinefield(normalisedCoordinates[0],normalisedCoordinates[1])
    }
    if (e.button === 2) {
        flagSquare(normalisedCoordinates[0],normalisedCoordinates[1]);
    }
    requestAnimationFrame(gameLoop);
}


canvas.addEventListener('mousedown', mouseClicked);

function mouseMoved(e) {
mouseCoordinates[0] = e.clientX - canvas.offsetLeft;
mouseCoordinates[1] = e.clientY - canvas.offsetTop;
}

canvas.addEventListener('mousemove', mouseMoved);
