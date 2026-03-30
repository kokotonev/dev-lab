
function MyButton({ count, onClick }: { count: number; onClick: () => void }) {
  return (
    <button className="button-base" onClick={onClick}>
      Clicked {count} times
    </button>
  );
}

export const MyFirstButton = MyButton;