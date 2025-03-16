import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, DollarSign, Coins, Calendar, HandCoins } from 'lucide-react';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import ErrorModal from "./ErrorModal.jsx";

const AddTransactionModal = ({ onClose, onSubmit, loading, openBoxes = [] }) => {
    const [formData, setFormData] = useState({
        coin_symbol: '',
        type: 'buy',
        price: '',
        amount: '',
        transaction_date: new Date(),
        fee: '',
    });

    const [errors, setErrors] = useState({});
    const [generalError, setGeneralError] = useState('');

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (errors[name]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }
    };

    const handleDateChange = (date) => {
        setFormData(prev => ({
            ...prev,
            transaction_date: date
        }));
    };

    const handleAllAmount = () => {
        // Find the coin in openBoxes that matches the entered coin_symbol
        const matchingCoin = openBoxes.find(
            box => box.coin_symbol.toLowerCase() === formData.coin_symbol.toLowerCase()
        );

        // Set the amount to the coin's amount or 0 if not found
        setFormData(prev => ({
            ...prev,
            amount: matchingCoin ? matchingCoin.amount : '0'
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setErrors({});
        setGeneralError('');

        const newErrors = {};
        if (!formData.coin_symbol) newErrors.coin_symbol = ['Coin symbol is required'];
        if (!formData.price || isNaN(formData.price)) newErrors.price = ['Valid price is required'];
        if (!formData.amount || isNaN(formData.amount)) newErrors.amount = ['Valid amount is required'];

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        try {
            const formattedDate = formData.transaction_date.toISOString().slice(0, 16).replace('T', ' ');
            const response = await onSubmit({
                ...formData,
                price: formData.price.toString(),
                amount: formData.amount.toString(),
                transaction_date: formattedDate
            });

            if (response?.data) {
                if (!response.data.success) {
                    setGeneralError(response.data.message);

                    if (response.data.data && typeof response.data.data === 'object') {
                        const fieldErrors = {};
                        Object.entries(response.data.data).forEach(([key, value]) => {
                            fieldErrors[key] = Array.isArray(value) ? value : [value];
                        });
                        setErrors(fieldErrors);
                    }
                }
            }
        } catch (error) {
            console.error('Transaction error:', error);
            setGeneralError('An unexpected error occurred');
        }
    };

    const TypeSwitch = () => (
        <div className="bg-gray-700 p-1 rounded-xl flex gap-1">
            <AnimatePresence mode="wait">
                {['buy', 'sell'].map((type) => (
                    <motion.button
                        key={type}
                        type="button"
                        onClick={() => setFormData(prev => ({ ...prev, type }))}
                        className={`relative px-8 py-2 rounded-lg font-medium transition-colors ${
                            formData.type === type ? 'text-white' : 'text-gray-400'
                        }`}
                    >
                        {formData.type === type && (
                            <motion.div
                                layoutId="activeType"
                                className={`absolute inset-0 rounded-lg ${
                                    type === 'buy' ? 'bg-green-600' : 'bg-red-600'
                                }`}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                            />
                        )}
                        <span className="relative z-10">
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </span>
                    </motion.button>
                ))}
            </AnimatePresence>
        </div>
    );

    return (
        <AnimatePresence mode="wait">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            >
                <motion.div
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: 20 }}
                    className="bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-xl border border-gray-700"
                >
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-bold text-white">Add Transaction</h2>
                        <motion.button
                            whileHover={{scale: 1.1}}
                            whileTap={{scale: 0.95}}
                            onClick={onClose}
                            className="p-2 hover:bg-gray-700 rounded-full transition-colors"
                        >
                            <X className="h-5 w-5 text-gray-400"/>
                        </motion.button>
                    </div>

                    <AnimatePresence>
                        {generalError && (
                            <ErrorModal error={generalError} onClose={() => setGeneralError("")}/>
                        )}
                    </AnimatePresence>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Transaction Type Switch */}
                        <div className="flex justify-center mb-6">
                            <TypeSwitch/>
                        </div>

                        {/* Coin Symbol Input */}
                        <div className="space-y-1">
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Coins className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="text"
                                    name="coin_symbol"
                                    placeholder="Coin Symbol (e.g., BTC)"
                                    value={formData.coin_symbol}
                                    onChange={handleInputChange}
                                    className={`w-full bg-gray-700 text-white rounded-xl pl-10 pr-4 py-3 focus:ring-2 ${
                                        formData.type === 'buy' ? 'focus:ring-green-500' : 'focus:ring-red-500'
                                    } outline-none transition-all ${
                                        errors.coin_symbol ? 'border-2 border-red-500' : 'border-transparent'
                                    }`}
                                />
                            </div>
                            {errors.coin_symbol && errors.coin_symbol.map((error, index) => (
                                <motion.p
                                    key={index}
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="text-red-500 text-sm pl-2"
                                >
                                    {error}
                                </motion.p>
                            ))}
                        </div>

                        {/* Price Input */}
                        <div className="space-y-1">
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <DollarSign className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="number"
                                    name="price"
                                    step="0.000001"
                                    placeholder="Price per coin"
                                    value={formData.price}
                                    onChange={handleInputChange}
                                    className={`w-full bg-gray-700 text-white rounded-xl pl-10 pr-4 py-3 focus:ring-2 ${
                                        formData.type === 'buy' ? 'focus:ring-green-500' : 'focus:ring-red-500'
                                    } outline-none transition-all ${
                                        errors.price ? 'border-2 border-red-500' : 'border-transparent'
                                    }`}
                                />
                            </div>
                            {errors.price && errors.price.map((error, index) => (
                                <motion.p
                                    key={index}
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="text-red-500 text-sm pl-2"
                                >
                                    {error}
                                </motion.p>
                            ))}
                        </div>

                        {/* Amount Input */}
                        <div className="space-y-1">
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Coins className="h-5 w-5 text-gray-400" />
                                </div>
                                <div className="flex">
                                    <input
                                        type="number"
                                        name="amount"
                                        step="0.000001"
                                        placeholder="Amount"
                                        value={formData.amount}
                                        onChange={handleInputChange}
                                        className={`w-full bg-gray-700 text-white rounded-l-xl pl-10 pr-4 py-3 focus:ring-2 ${
                                            formData.type === 'buy' ? 'focus:ring-green-500' : 'focus:ring-red-500'
                                        } outline-none transition-all ${
                                            errors.amount ? 'border-2 border-red-500' : 'border-transparent'
                                        }`}
                                    />
                                    {formData.type === 'sell' && (
                                        <motion.button
                                            type="button"
                                            onClick={handleAllAmount}
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            className={`bg-red-600 text-white rounded-r-xl px-4 py-3 font-medium hover:opacity-90 transition-all`}
                                        >
                                            All
                                        </motion.button>
                                    )}
                                </div>
                            </div>
                            {errors.amount && errors.amount.map((error, index) => (
                                <motion.p
                                    key={index}
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="text-red-500 text-sm pl-2"
                                >
                                    {error}
                                </motion.p>
                            ))}
                        </div>

                        {/* Fee and Date Picker in One Row */}
                        <div className="flex gap-4">
                            {/* Fee Percentage */}
                            <div className="relative w-1/2">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <HandCoins className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="number"
                                    name="fee"
                                    step="0.000001"
                                    placeholder="Fee %"
                                    value={formData.fee}
                                    onChange={handleInputChange}
                                    className={`w-full bg-gray-700 text-white rounded-xl pl-10 pr-4 py-3 focus:ring-2 ${
                                        formData.type === 'buy' ? 'focus:ring-green-500' : 'focus:ring-red-500'
                                    } outline-none transition-all ${
                                        errors.fee ? 'border-2 border-red-500' : 'border-transparent'
                                    }`}
                                />
                                {errors.fee && errors.fee.map((error, index) => (
                                    <motion.p
                                        key={index}
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="text-red-500 text-sm pl-2"
                                    >
                                        {error}
                                    </motion.p>
                                ))}
                            </div>

                            {/* Date Picker */}
                            <div className="relative w-1/2">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Calendar className="h-5 w-5 text-gray-400" />
                                </div>
                                <DatePicker
                                    selected={formData.transaction_date}
                                    onChange={handleDateChange}
                                    showTimeSelect
                                    timeFormat="HH:mm"
                                    timeIntervals={15}
                                    dateFormat="yyyy-MM-dd HH:mm"
                                    className={`w-full bg-gray-700 text-white rounded-xl pl-10 pr-4 py-3 focus:ring-2 ${
                                        formData.type === 'buy' ? 'focus:ring-green-500' : 'focus:ring-red-500'
                                    } outline-none transition-all`}
                                />
                            </div>
                        </div>


                        <motion.button
                            type="submit"
                            disabled={loading}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className={`w-full ${
                                formData.type === 'buy' ? 'bg-green-600' : 'bg-red-600'
                            } text-white rounded-xl px-4 py-3 font-medium hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg ${
                                formData.type === 'buy' ? 'hover:shadow-green-500/30' : 'hover:shadow-red-500/30'
                            }`}
                        >
                            {loading ? (
                                <div className="flex items-center justify-center">
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                                    Processing...
                                </div>
                            ) : (
                                `${formData.type === 'buy' ? 'Buy' : 'Sell'} Transaction`
                            )}
                        </motion.button>
                    </form>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};

export default AddTransactionModal;