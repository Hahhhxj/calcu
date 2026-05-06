let display = document.getElementById('result');
let firstNumber = '';
let operator = '';
let secondNumber = '';
let isOperatorClicked = false;
let isConnected = false;
let currentUser = null;

function checkConnection() {
    fetch('http://localhost:5001/api/health')
        .then(response => {
            if (response.ok) {
                isConnected = true;
                document.querySelector('.status').textContent = '后端服务: 已连接';
                document.querySelector('.status').style.color = '#27ae60';
            } else {
                isConnected = false;
                document.querySelector('.status').textContent = '后端服务: 未连接';
                document.querySelector('.status').style.color = '#e74c3c';
            }
        })
        .catch(() => {
            isConnected = false;
            document.querySelector('.status').textContent = '后端服务: 未连接';
            document.querySelector('.status').style.color = '#e74c3c';
        });
}

checkConnection();

function appendNumber(num) {
    if (isOperatorClicked) {
        if (secondNumber.length < 2) {
            secondNumber += num;
            display.value = firstNumber + ' ' + operator + ' ' + secondNumber;
        }
    } else {
        if (firstNumber.length < 2) {
            firstNumber += num;
            display.value = firstNumber;
        }
    }
}

function appendOperator(op) {
    if (firstNumber !== '') {
        operator = op;
        isOperatorClicked = true;
        display.value = firstNumber + ' ' + op + ' ';
    }
}

function calculate() {
    if (firstNumber !== '' && operator !== '' && secondNumber !== '') {
        const expression = firstNumber + operator + secondNumber;

        if (isConnected) {
            fetch('http://localhost:5001/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ expression })
            })
            .then(response => response.json())
            .then(data => {
                if (data.result !== undefined) {
                    display.value = data.result;
                    firstNumber = data.result.toString();
                    secondNumber = '';
                    operator = '';
                    isOperatorClicked = false;
                }
            })
            .catch(() => {
                localCalculate();
            });
        } else {
            localCalculate();
        }
    }
}

function localCalculate() {
    let num1 = parseFloat(firstNumber);
    let num2 = parseFloat(secondNumber);
    let result = 0;

    switch (operator) {
        case '+':
            result = num1 + num2;
            break;
        case '-':
            result = num1 - num2;
            break;
        case '*':
            result = num1 * num2;
            break;
        case '/':
            result = num1 / num2;
            break;
    }

    display.value = result;
    firstNumber = result.toString();
    secondNumber = '';
    operator = '';
    isOperatorClicked = false;
}

function clearDisplay() {
    display.value = '0';
    firstNumber = '';
    secondNumber = '';
    operator = '';
    isOperatorClicked = false;
}

function backspace() {
    if (isOperatorClicked) {
        if (secondNumber !== '') {
            secondNumber = secondNumber.slice(0, -1);
            display.value = firstNumber + ' ' + operator + ' ' + (secondNumber || '');
        }
    } else {
        if (firstNumber !== '') {
            firstNumber = firstNumber.slice(0, -1);
            display.value = firstNumber || '0';
        }
    }
}

function appendDecimal() {
    if (isOperatorClicked) {
        if (secondNumber !== '' && !secondNumber.includes('.')) {
            secondNumber += '.';
            display.value = firstNumber + ' ' + operator + ' ' + secondNumber;
        }
    } else {
        if (firstNumber !== '' && !firstNumber.includes('.')) {
            firstNumber += '.';
            display.value = firstNumber;
        }
    }
}

function openLoginModal() {
    document.getElementById('login-modal').style.display = 'block';
    document.getElementById('login-message').textContent = '';
}

function openRegisterModal() {
    document.getElementById('register-modal').style.display = 'block';
    document.getElementById('register-message').textContent = '';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('http://localhost:5001/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.user) {
            currentUser = data.user;
            updateUserStatus();
            closeModal('login-modal');
            alert('登录成功');
        } else {
            document.getElementById('login-message').textContent = data.error || '登录失败';
        }
    })
    .catch(() => {
        document.getElementById('login-message').textContent = '登录失败，请检查网络连接';
    });
}

function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;

    fetch('http://localhost:5001/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === '注册成功') {
            closeModal('register-modal');
            alert('注册成功，请登录');
        } else {
            document.getElementById('register-message').textContent = data.error || '注册失败';
        }
    })
    .catch(() => {
        document.getElementById('register-message').textContent = '注册失败，请检查网络连接';
    });
}

function logout() {
    currentUser = null;
    updateUserStatus();
    alert('已退出登录');
}

function updateUserStatus() {
    const userStatus = document.getElementById('user-status');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');

    if (currentUser) {
        userStatus.textContent = `已登录: ${currentUser.username}`;
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
    } else {
        userStatus.textContent = '未登录';
        loginBtn.style.display = 'inline-block';
        registerBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
    }
}

function calculate() {
    if (firstNumber !== '' && operator !== '' && secondNumber !== '') {
        const expression = firstNumber + operator + secondNumber;

        if ((operator === '*' || operator === '/') && !currentUser) {
            alert('乘法和除法运算需要登录');
            openLoginModal();
            return;
        }

        if (isConnected) {
            fetch('http://localhost:5001/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    expression,
                    user_id: currentUser ? currentUser.id : null
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.result !== undefined) {
                    display.value = data.result;
                    firstNumber = data.result.toString();
                    secondNumber = '';
                    operator = '';
                    isOperatorClicked = false;
                } else if (data.error) {
                    alert(data.error);
                    if (data.error.includes('需要登录')) {
                        openLoginModal();
                    }
                }
            })
            .catch(() => {
                localCalculate();
            });
        } else {
            localCalculate();
        }
    }
}

function showHistory() {
    if (!currentUser) {
        alert('查看历史记录需要登录');
        openLoginModal();
        return;
    }

    if (isConnected) {
        fetch('http://localhost:5001/api/history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: currentUser.id })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                let historyHTML = '<h3>计算历史记录</h3><ul>';
                data.forEach(item => {
                    historyHTML += `<li>${item.expression} = ${item.result} (${item.created_at})</li>`;
                });
                historyHTML += '</ul>';
                alert(historyHTML);
            }
        })
        .catch(() => {
            alert('获取历史记录失败');
        });
    } else {
        alert('后端服务未连接，无法获取历史记录');
    }
}

document.querySelector('.history').addEventListener('click', showHistory);

window.onclick = function(event) {
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');
    if (event.target == loginModal) {
        loginModal.style.display = 'none';
    }
    if (event.target == registerModal) {
        registerModal.style.display = 'none';
    }
}
