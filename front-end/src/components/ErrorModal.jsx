import React from 'react';
import { motion } from "framer-motion";
import { X, AlertCircle } from "lucide-react";

const ErrorModal = ({ error, onClose }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            transition={{
                duration: 0.2,
                ease: "easeOut"
            }}
            className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-md px-4"
            >
            <div className="relative flex items-center gap-3 w-full rounded-lg border border-red-200 bg-red-50 p-4 shadow-lg">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <span className="text-red-600 text-sm font-medium">
                  {error}
                </span>
                <button
                    onClick={onClose}
                    className="absolute right-2 top-2 p-1 rounded-md hover:bg-red-100 transition-colors"
                >
                    <X className="h-4 w-4 text-red-600" />
                </button>
            </div>
        </motion.div>
    );
};

export default ErrorModal;