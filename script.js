let display = document.getElementById('result');
let firstNumber = '';
let operator = '';
let secondNumber = '';
let isOperatorClicked = false;
let isConnected = false;
let currentUser = null;
let isVip = false;

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

        if ((operator === '*' || operator === '/') && !currentUser) {
            alert('乘法和除法运算需要登录');
            openLoginModal();
            return;
        }

        if (operator === '/' && !isVip) {
            alert('除法运算需要注册VIP');
            openVipModal();
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
                    } else if (data.error.includes('需要注册VIP')) {
                        openVipModal();
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

function openVipModal() {
    if (!currentUser) {
        alert('请先登录');
        openLoginModal();
        return;
    }
    document.getElementById('vip-modal').style.display = 'block';
    document.getElementById('vip-message').textContent = '';
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
            isVip = data.user.is_vip || false;
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

function handleVipRegister(event) {
    event.preventDefault();
    
    const gender = document.querySelector('input[name="gender"]:checked')?.value;
    const phone = document.getElementById('vip-phone').value;
    const birthday = document.getElementById('vip-birthday').value;
    const agree = document.getElementById('vip-agree').checked;

    if (!gender) {
        document.getElementById('vip-message').textContent = '请选择性别';
        return;
    }

    if (!phone) {
        document.getElementById('vip-message').textContent = '请填写手机号码';
        return;
    }

    if (!birthday) {
        document.getElementById('vip-message').textContent = '请选择生日';
        return;
    }

    if (!agree) {
        document.getElementById('vip-message').textContent = '请勾选同意注册VIP';
        return;
    }

    fetch('http://localhost:5001/api/register_vip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: currentUser.id,
            gender: gender,
            phone: phone,
            birthday: birthday,
            agree: agree
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'VIP注册成功') {
            isVip = true;
            currentUser.is_vip = true;
            updateUserStatus();
            closeModal('vip-modal');
            alert('VIP注册成功！您现在可以使用除法运算了');
        } else {
            document.getElementById('vip-message').textContent = data.error || 'VIP注册失败';
        }
    })
    .catch(() => {
        document.getElementById('vip-message').textContent = 'VIP注册失败，请检查网络连接';
    });
}

function logout() {
    currentUser = null;
    isVip = false;
    updateUserStatus();
    alert('已退出登录');
}

function updateUserStatus() {
    const userStatus = document.getElementById('user-status');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const vipBtn = document.getElementById('vip-btn');
    const vipHint = document.getElementById('vip-hint');

    if (currentUser) {
        if (isVip) {
            userStatus.textContent = `已登录: ${currentUser.username} (VIP)`;
            vipBtn.style.display = 'none';
            vipHint.textContent = '您是VIP用户，可以使用除法运算';
            vipHint.style.color = '#f39c12';
        } else {
            userStatus.textContent = `已登录: ${currentUser.username}`;
            vipBtn.style.display = 'inline-block';
            vipHint.textContent = '注册VIP可解锁除法运算功能';
            vipHint.style.color = '#3498db';
        }
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        logoutBtn.style.display = 'inline-block';
    } else {
        userStatus.textContent = '未登录';
        vipBtn.style.display = 'none';
        vipHint.textContent = '';
        loginBtn.style.display = 'inline-block';
        registerBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'none';
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
    const vipModal = document.getElementById('vip-modal');
    if (event.target == loginModal) {
        loginModal.style.display = 'none';
    }
    if (event.target == registerModal) {
        registerModal.style.display = 'none';
    }
    if (event.target == vipModal) {
        vipModal.style.display = 'none';
    }
}
