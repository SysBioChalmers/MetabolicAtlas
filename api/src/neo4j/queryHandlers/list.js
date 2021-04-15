import driver from 'neo4j/driver';

const queryListResult = async (statement) => {
  const session = driver.session();

  let result;
  let error;

  try {
    const response = await session.readTransaction(t => t.run(statement));
    result = response.records.map((r) => r.get(0));
  } catch (e) {
    error = e;
  } finally {
    await session.close();
  }

  if (error) {
    throw error;
  }

  return result;
};

export default queryListResult;
