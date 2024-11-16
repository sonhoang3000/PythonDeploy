class PuzzleGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 3;
        this.tiles = [];
        this.tileSize = this.canvas.width / this.gridSize;
        this.image = null;
        this.imagePieces = [];
        this.showNumbers = true;
        this.hideZero = true;
        this.isAnimating = false;
        this.animationSpeed = 500;
        this.imageLoaded = false;
        this.initializePuzzle();
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
    }

    initializePuzzle() {
        this.tiles = [];
        for (let i = 0; i < this.gridSize * this.gridSize - 1; i++) {
            this.tiles.push(i + 1);
        }
        this.tiles.push(null);
        this.shuffle();
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                const index = i + j * this.gridSize;
                const value = this.tiles[index];
                
                if (value !== null) {
                    this.ctx.strokeStyle = '#000000';
                    this.ctx.lineWidth = 2;
                    this.ctx.strokeRect(
                        i * this.tileSize,
                        j * this.tileSize,
                        this.tileSize,
                        this.tileSize
                    );
                    
                    if (this.image && this.imagePieces.length > 0 && this.imageLoaded) {
                        const pieceIndex = value - 1;
                        if (pieceIndex >= 0 && pieceIndex < this.imagePieces.length) {
                            const img = this.imagePieces[pieceIndex];
                            this.ctx.drawImage(
                                img,
                                i * this.tileSize,
                                j * this.tileSize,
                                this.tileSize,
                                this.tileSize
                            );
                        }
                    }
                    
                    if ((this.showNumbers || !this.image || !this.imageLoaded) && 
                        (!this.hideZero || value !== 0)) {
                        this.drawNumber(value, i, j);
                    }
                }
            }
        }
    }

    drawNumber(value, i, j) {
        this.ctx.font = '30px Arial';
        this.ctx.fillStyle = '#000000';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(
            value.toString(),
            i * this.tileSize + this.tileSize/2,
            j * this.tileSize + this.tileSize/2
        );
    }

    handleClick(e) {
        if (this.isAnimating) return;

        const rect = this.canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;
        
        const tileX = Math.floor(clickX / this.tileSize);
        const tileY = Math.floor(clickY / this.tileSize);
        
        const emptyIndex = this.tiles.indexOf(null);
        const emptyX = emptyIndex % this.gridSize;
        const emptyY = Math.floor(emptyIndex / this.gridSize);
        
        if (this.canMove(tileX, tileY, emptyX, emptyY)) {
            this.moveTile(tileX, tileY, emptyX, emptyY);
            updateScore(-20);
            this.draw();
            
            if (this.isComplete()) {
                setTimeout(() => {
                    showWinnerPopup(score);
                }, 100);
            }
        }
    }

    canMove(tileX, tileY, emptyX, emptyY) {
        return (
            (Math.abs(tileX - emptyX) === 1 && tileY === emptyY) ||
            (Math.abs(tileY - emptyY) === 1 && tileX === emptyX)
        );
    }

    moveTile(tileX, tileY, emptyX, emptyY) {
        const tileIndex = tileX + tileY * this.gridSize;
        const emptyIndex = emptyX + emptyY * this.gridSize;
        
        [this.tiles[tileIndex], this.tiles[emptyIndex]] = 
        [this.tiles[emptyIndex], this.tiles[tileIndex]];
    }

    isComplete() {
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                const index = i + j * this.gridSize;
                const expectedValue = index + 1;
                
                if (index === this.tiles.length - 1) {
                    if (this.tiles[index] !== null) {
                        return false;
                    }
                } 
                else if (this.tiles[index] !== expectedValue) {
                    return false;
                }
            }
        }
        return true;
    }

    shuffle() {
        if (this.isAnimating) return;
        
        if (!this.imageLoaded && this.image) {
            alert('Vui lòng đợi ảnh được tải hoàn tất!');
            return;
        }

        let moves = 100;
        while (moves > 0) {
            const emptyIndex = this.tiles.indexOf(null);
            const emptyX = emptyIndex % this.gridSize;
            const emptyY = Math.floor(emptyIndex / this.gridSize);
            
            const possibleMoves = [];
            
            const directions = [
                {x: -1, y: 0},
                {x: 1, y: 0},
                {x: 0, y: -1},
                {x: 0, y: 1}
            ];
            
            for (const dir of directions) {
                const newX = emptyX + dir.x;
                const newY = emptyY + dir.y;
                
                if (newX >= 0 && newX < this.gridSize && 
                    newY >= 0 && newY < this.gridSize) {
                    possibleMoves.push({x: newX, y: newY});
                }
            }
            
            if (possibleMoves.length > 0) {
                const move = possibleMoves[Math.floor(Math.random() * possibleMoves.length)];
                this.moveTile(move.x, move.y, emptyX, emptyY);
                moves--;
            }
        }
        this.draw();
    }

    changeSize(size) {
        this.gridSize = size;
        this.tileSize = this.canvas.width / this.gridSize;
        this.initializePuzzle();
        if (this.image && this.imageLoaded) {
            this.loadAndCutImage(this.image);
        }
    }

    async loadAndCutImage(img) {
        this.image = img;
        this.imagePieces = [];
        this.imageLoaded = false;
        
        try {
            const pieceWidth = img.width / this.gridSize;
            const pieceHeight = img.height / this.gridSize;
            
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');
            tempCanvas.width = pieceWidth;
            tempCanvas.height = pieceHeight;

            for (let y = 0; y < this.gridSize; y++) {
                for (let x = 0; x < this.gridSize; x++) {
                    tempCtx.clearRect(0, 0, pieceWidth, pieceHeight);
                    tempCtx.drawImage(
                        img,
                        x * pieceWidth, y * pieceHeight,
                        pieceWidth, pieceHeight,
                        0, 0,
                        pieceWidth, pieceHeight
                    );
                    
                    const pieceImage = new Image();
                    await new Promise((resolve) => {
                        pieceImage.onload = resolve;
                        pieceImage.src = tempCanvas.toDataURL();
                    });
                    this.imagePieces.push(pieceImage);
                }
            }
            
            this.imageLoaded = true;
            this.draw();
        } catch (error) {
            console.error('Lỗi khi xử lý ảnh:', error);
            this.imageLoaded = false;
            this.image = null;
            this.imagePieces = [];
        }
    }

    async animateSolution(solution) {
        this.isAnimating = true;
        try {
            for (let i = 0; i < solution.length; i++) {
                if (!this.isAnimating) break;
                
                this.tiles = Array.from(solution[i]); // Chuyển đổi thành array
                this.tiles = this.tiles.map(val => val === 0 ? null : val); // Chuyển 0 thành null
                this.draw();
                await new Promise(resolve => setTimeout(resolve, this.animationSpeed));
            }
        } finally {
            this.isAnimating = false;
        }
    }

    stopAnimation() {
        this.isAnimating = false;
    }

    async solvePuzzle() {
        if (this.isAnimating) {
            this.stopAnimation();
            return;
        }

        updateButtons(true);

        try {
            const currentState = this.tiles.map(tile => tile === null ? 0 : tile);
            
            const response = await fetch('/api/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: this.gridSize === 3 ? '3x3' : '4x4',
                    currentState: currentState
                })
            });

            const data = await response.json();
            if (data.solution && data.solution.length > 0) {
                await this.animateSolution(data.solution);
                if (this.isAnimating && this.isComplete()) {
                    alert(`Chúc mừng! Puzzle đã được giải!\nĐiểm số: ${score}`);
                    setTimeout(() => {
                        this.resetGame();
                        score = 1000;
                        document.getElementById('score').textContent = score;
                    }, 1000);
                }
            } else {
                alert('Không tìm thấy giải pháp!');
            }
        } catch (error) {
            if (this.isAnimating) {
                console.error('Lỗi khi giải puzzle:', error);
                alert('Có lỗi xảy ra khi giải puzzle!');
            }
        } finally {
            updateButtons(false);
        }
    }

    resetGame() {
        this.isAnimating = false;
        this.initializePuzzle();
        this.draw();
    }

    checkWinCondition() {
        if (this.isComplete()) {
            setTimeout(() => {
                showWinnerPopup(score);
            }, 100);
        }
    }
}

let game;
window.onload = function() {
    game = new PuzzleGame();
    document.getElementById('showNumbers').checked = game.showNumbers;
    score = 1000;
    document.getElementById('score').textContent = score;
};

function shuffle() {
    if (!game.isAnimating) {
        game.shuffle();
        score = 1000;
        document.getElementById('score').textContent = score;
    }
}

function solve() {
    game.solvePuzzle();
}

function stopSolving() {
    game.stopAnimation();
    updateButtons(false);
}

function loadImage() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    
    input.onchange = async function(e) {
        const file = e.target.files[0];
        if (file) {
            try {
                const reader = new FileReader();
                const imageLoadPromise = new Promise((resolve, reject) => {
                    reader.onload = function(event) {
                        const img = new Image();
                        img.onload = () => resolve(img);
                        img.onerror = reject;
                        img.src = event.target.result;
                        
                        // Hiển thị ảnh gốc
                        const originalImage = document.getElementById('originalImage');
                        originalImage.src = event.target.result;
                        originalImage.style.display = 'block';
                    };
                    reader.onerror = reject;
                });
                
                reader.readAsDataURL(file);
                const loadedImage = await imageLoadPromise;
                
                const tempCanvas = document.createElement('canvas');
                const tempCtx = tempCanvas.getContext('2d');
                tempCanvas.width = game.canvas.width;
                tempCanvas.height = game.canvas.height;
                
                tempCtx.drawImage(loadedImage, 0, 0, tempCanvas.width, tempCanvas.height);
                
                const resizedImage = new Image();
                await new Promise((resolve) => {
                    resizedImage.onload = resolve;
                    resizedImage.src = tempCanvas.toDataURL();
                });
                
                await game.loadAndCutImage(resizedImage);
            } catch (error) {
                console.error('Lỗi khi tải ảnh:', error);
                alert('Có lỗi xảy ra khi tải ảnh. Vui lòng thử lại.');
            }
        }
    };
    
    input.click();
}

function changePuzzle(type) {
    if (!game.isAnimating) {
        const size = type === '3x3' ? 3 : 4;
        game.changeSize(size);
        score = 1000;
        document.getElementById('score').textContent = score;
    }
}

function resetGame() {
    game.resetGame();
    score = 1000;
    document.getElementById('score').textContent = score;
}

window.showWinnerPopup = function(score) {
    console.log("Showing winner popup with score:", score);
    const popup = document.getElementById('winnerPopup');
    const finalScore = document.getElementById('finalScore');
    finalScore.textContent = score;
    popup.style.display = 'block';
    createConfetti();
    
    // Thêm gọi API lưu điểm số
    fetch('/api/save-score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            score: score,
            type: game.gridSize === 3 ? '3x3' : '4x4'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            console.error('Lỗi khi lưu điểm số:', data.error);
        }
    })
    .catch(error => {
        console.error('Lỗi khi gọi API:', error);
    });
}

window.closeWinnerPopup = function() {
    const popup = document.getElementById('winnerPopup');
    popup.style.display = 'none';
    game.resetGame();
    score = 1000;
    document.getElementById('score').textContent = score;
}

window.createConfetti = function() {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animation = `confetti ${Math.random() * 3 + 2}s ease-in-out infinite`;
        document.body.appendChild(confetti);
        
        setTimeout(() => confetti.remove(), 5000);
    }
}

// Thêm hàm xóa lịch sử
async function deleteGameHistory() {
    try {
        const response = await fetch('/api/delete-history', {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            // Xóa nội dung hiển thị trong historyList
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';
            alert('Đã xóa lịch sử thành công!');
        } else {
            alert('Không thể xóa lịch sử: ' + data.error);
        }
    } catch (error) {
        console.error('Lỗi khi xóa lịch sử:', error);
        alert('Có lỗi xảy ra khi xóa lịch sử!');
    }
}