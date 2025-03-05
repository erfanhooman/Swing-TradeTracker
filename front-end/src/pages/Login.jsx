import { useState } from 'react';
import { LoginApi } from '../api';
import { motion } from 'framer-motion';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [fieldErrors, setFieldErrors] = useState({});
    const [touched, setTouched] = useState({ username: false, password: false });


    const handleLogin = async (event) => {
        event.preventDefault();
        setError('');
        setFieldErrors({});

        try {
            const response = await LoginApi({ username, password });

            if (response.status === 200 && response.data.success) {
                window.location.reload();
            } else {
                handleErrors(response);
            }
        } catch (err) {
            console.error('Login error:', err);
            setError(err.toString() || 'An unexpected error occurred. Please try again.');
        }
    };

    const handleErrors = (response) => {

        if (response.status === 400) {
            setFieldErrors(response.data.data || {});
            setError('');
        } else if (response.status === 401 || response.status === 500) {
            setFieldErrors({});
            setError(response.data.message || 'Something went wrong.');
        }
    };

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-white p-8 rounded-lg shadow-lg w-full max-w-sm"
            >
                <h2 className="text-2xl font-semibold text-center text-gray-700 mb-6">Login</h2>

                <form onSubmit={handleLogin} className="space-y-4">
                    {/* Username Field */}
                    <div>
                        <input
                            type="text"
                            placeholder="Username"
                            value={username}
                            required
                            onBlur={() => setTouched({ ...touched, username: true })}
                            onChange={(e) => setUsername(e.target.value)}
                            className={`w-full px-4 py-2 border rounded-md focus:outline-none transition-all duration-300
                                ${fieldErrors.username || (touched.username && !username) ? 'border-red-500' : 'border-gray-300'}
                                focus:ring-2 focus:ring-blue-500`}
                        />
                        {fieldErrors.username && (
                            <motion.small
                                initial={{ opacity: 0, y: -5 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="text-red-500 text-sm"
                            >
                                {fieldErrors.username[0]}
                            </motion.small>
                        )}
                        {touched.username && !username && (
                            <motion.small
                                initial={{ opacity: 0, y: -5 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="text-red-500 text-sm"
                            >
                                Username is required.
                            </motion.small>
                        )}
                    </div>

                    {/* Password Field */}
                    <div>
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            required
                            onBlur={() => setTouched({ ...touched, password: true })}
                            onChange={(e) => setPassword(e.target.value)}
                            className={`w-full px-4 py-2 border rounded-md focus:outline-none transition-all duration-300
                                ${fieldErrors.password || (touched.password && !password) ? 'border-red-500' : 'border-gray-300'}
                                focus:ring-2 focus:ring-blue-500`}
                        />
                        {fieldErrors.password && (
                            <motion.small
                                initial={{ opacity: 0, y: -5 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="text-red-500 text-sm"
                            >
                                {fieldErrors.password[0]}
                            </motion.small>
                        )}
                        {touched.password && !password && (
                            <motion.small
                                initial={{ opacity: 0, y: -5 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="text-red-500 text-sm"
                            >
                                Password is required.
                            </motion.small>
                        )}
                    </div>

                    {/* Error Message */}
                    {error && (
                        <motion.p
                            initial={{ opacity: 0, y: -5 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="text-red-600 text-sm text-center font-medium bg-red-100 p-2 rounded"
                        >
                            {error}
                        </motion.p>
                    )}

                    {/* Submit Button */}
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        type="submit"
                        className="w-full py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all"
                    >
                        Login
                    </motion.button>
                </form>
            </motion.div>
        </div>
    );
}

export default Login;
