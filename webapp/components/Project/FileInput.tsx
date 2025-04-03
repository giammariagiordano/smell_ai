import React, { useRef, useEffect } from "react";

type FileInputProps = {
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

const FileInput: React.FC<FileInputProps> = ({ onChange }) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (fileInputRef.current) {
      (fileInputRef.current as HTMLInputElement).webkitdirectory = true;
    }
  }, []);

  return (
    <input
      ref={fileInputRef}
      type="file"
      onChange={onChange}
      className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-100 transition-all duration-300"
      multiple
    />
  );
};

export default FileInput;
