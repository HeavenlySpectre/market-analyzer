import type { InputHTMLAttributes } from "react";
import { forwardRef } from "react";
import { clsx } from "clsx";

interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "className"> {
  className?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <div className="w-full">
        <input
          ref={ref}
          className={clsx(
            "w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg",
            "text-gray-100 placeholder-gray-400",
            "focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            "transition-colors duration-200",
            error && "border-red-500 focus:ring-red-500",
            className
          )}
          {...props}
        />
        {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
