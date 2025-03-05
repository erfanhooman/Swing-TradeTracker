// src/components/TransactionModal.jsx
import { motion } from "framer-motion";
import { X } from "lucide-react";

const TransactionModal = ({
                              transactionType,
                              amount,
                              setAmount,
                              handleTransaction,
                              loading,
                              onClose,
                          }) => {
    return (
        <motion.div
            key="transaction"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="w-64 h-30 p-4 bg-gray-800 rounded-lg shadow-xl flex flex-col justify-center"
        >
            <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Enter amount"
                className="w-full mb-2.5 p-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:border-violet-500"
            />
            <div className="flex gap-2">
                <button
                    onClick={handleTransaction}
                    disabled={loading}
                    className={`flex-1 p-1 rounded font-medium transition-colors ${
                        transactionType === "deposit"
                            ? "bg-green-600 hover:bg-green-700"
                            : "bg-red-600 hover:bg-red-700"
                    } text-white`}
                >
                    {loading ? "Processing..." : transactionType}
                </button>
                <button
                    onClick={onClose}
                    className={`w-10 p-2 rounded font-medium transition-colors ${
                        transactionType === "deposit"
                            ? "bg-green-600 hover:bg-green-700"
                            : "bg-red-600 hover:bg-red-700"
                    } text-white`}
                >
                    <X className="h-5 w-5" />
                </button>
            </div>
        </motion.div>
    );
};

export default TransactionModal;
