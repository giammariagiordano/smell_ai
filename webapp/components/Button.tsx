// components/Button.tsx
import React from "react";

type ButtonProps = {
  onClick: () => void;
  children: React.ReactNode;
  className: string;
  disabled: boolean;
};

const Button: React.FC<ButtonProps> = ({ onClick, children, className, disabled }) => {
  return (
    <button
      onClick={onClick}
      className={`transition-all duration-300 transform rounded-xl font-semibold ${className} ${
        disabled ? "cursor-not-allowed" : "hover:scale-105"
      }`}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default Button;
