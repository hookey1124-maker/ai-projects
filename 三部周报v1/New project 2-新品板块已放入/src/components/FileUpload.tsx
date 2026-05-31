import { Upload } from 'lucide-react';

type FileUploadProps = {
  onFile: (file: File) => void;
};

export default function FileUpload({ onFile }: FileUploadProps) {
  return (
    <label className="upload-button">
      <Upload size={16} />
      上传 Excel
      <input
        type="file"
        accept=".xlsx,.xls"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onFile(file);
          event.currentTarget.value = '';
        }}
      />
    </label>
  );
}
