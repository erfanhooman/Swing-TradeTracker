import { motion } from "framer-motion";

const LoadingSpinner = () => {
    return (
        <motion.div
            className="w-12 h-12 border-4 border-t-4 border-gray-600 border-t-transparent rounded-full animate-spin"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
        />
    );
};

export default LoadingSpinner;
