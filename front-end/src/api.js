// api.js
import axios from 'axios';
const apiUrl = import.meta.env.VITE_API_URL;

const url = axios.create({
    baseURL: apiUrl,
    validateStatus: (status) => true,
});

export function LoginApi(value) {
    return url.post('/auth/login/', value)
        .then((res) => {
            if (res.status >= 200 && res.status < 300) {
                const accessToken = res.data.data.access;
                const refreshToken = res.data.data.refresh;

                url.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
                localStorage.setItem("accessToken", accessToken);
                localStorage.setItem("refreshToken", refreshToken);
            }
            return res;
        });
}

export function RefreshAccessToken() {
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
        const origin = new URL(window.location.href).origin;
        if (origin + '/' === window.location.href) return;
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        window.location.href = origin;
    }

    url.defaults.headers.common['Authorization'] = `Bearer ${refreshToken}`;

    return url
        .post('auth/token/refresh/', { refresh: refreshToken })
        .then((res) => {
            const accessToken = res.data.access;

            // Update the default header to the new access token
            url.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

            // Store the new access token
            localStorage.setItem('accessToken', accessToken);
        })
        .catch((error) => {
            throw error;
        });
}

export function BalanceApi() {
    return url.get('/balance/');
}

export function DepositApi(data) {
    return url.post('/balance/', data);
}

export function WithdrawApi(data) {
    return url.delete('/balance/', { data });
}

export function OpenBoxesList() {
    return url.get('/boxes/?closed=false');
}

export function CloseBoxesList() {
    return url.get('/boxes/?closed=true');
}

export function LogoutApi({ refresh }) {
    return url.post('/auth/logout/', { refresh });
}

export function TransactionsApi(id) {
    return url.get(`/boxes/${id}/transactions/`);
}

export function CloseBoxApi(id) {
    return url.patch(`/boxes/${id}/close/`);
}

export function TransactionApi(data) {
    return url.post(`/transactions/`, data);
}

export function DeleteTransactionApi(id) {
    return url.delete(`/transactions/${id}/`);
}

export function SummaryApi() {
    return url.get('/summary/');
}