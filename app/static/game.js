// Màu sắc và biến cấu hình
const XMAI = "#ff1493";
const BLACK = "#000000";
const PINK = "#ff69b4";
const BUTTON_COLOR = "#87ceeb";
const BORDER_WIDTH = 2;
const SOLUTION_SPEED = 300;

let gameGrid = document.getElementById("game-grid");
let gridSize = 3; // Kích thước mặc định là 3x3

// Khởi tạo trò chơi
function initializeGame(size) {
    gridSize = size;
    gameGrid.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`;
    gameGrid.innerHTML = ""; // Xóa các ô hiện có

    for (let i = 0; i < gridSize * gridSize; i++) {
        let cell = document.createElement("div");
        cell.className = "game-cell";
        cell.textContent = i + 1;
        if (i === gridSize * gridSize - 1) {
            cell.classList.add("empty"); // Ô trống
            cell.textContent = "";
        }
        gameGrid.appendChild(cell);
    }
}

// Hàm xáo trộn trò chơi
function shuffle() {
    alert("Shuffle clicked");
}

// Hàm giải quyết trò chơi
function solve() {
    alert("Solve clicked");
}

// Hàm thay đổi lưới 3x3
function changeTo3x3() {
    initializeGame(3);
}

// Hàm thay đổi lưới 4x4
function changeTo4x4() {
    initializeGame(4);
}

// Hàm load ảnh (phải thêm tính năng thực tế nếu muốn)
function loadImage() {
    alert("Load image clicked");
}

// Khởi tạo trò chơi mặc định 3x3 khi trang tải
window.onload = function() {
    initializeGame(3);
};
